from datetime import datetime
import pandas as pd
import os
import pdfplumber
from dataclasses import dataclass


_caminho_notas_rf = rf'C:\Users\Felipe Lima\Desktop\Felipe\Consultoria\Notas RF'
_caminho_rf_exportacao = rf'C:\Users\Felipe Lima\OneDrive\Python\administracao\carteira_rf'

_caminho_notas_bolsa = rf'C:\Users\Felipe Lima\Desktop\Felipe\Consultoria\Notas Bolsa'
_caminho_bolsa_exportacao = rf'C:\Users\Felipe Lima\OneDrive\Python\administracao\carteira_bolsa'

dicionario_ativos = {"ISHARE SP500": 'IVVB11',
                     "TREND NASDAQ": 'NASD11'}


@dataclass()
class TxtPDF:
    string: str

    @property
    def num(self):
        return round(float(self.string.replace('.', '').replace(',', '.')), 13)

    @property
    def emissor(self):
        string = self.string
        for palavra in ['BANCO', 'S/A', '-', 'Emissor', 'S.A.', '.', ' DE', ' INV', ' E']:
            string = string.replace(palavra, '').strip()
        return ' '.join(string.split(' ')[:2])

    @property
    def indexador(self):
        string = self.string.upper()
        if 'CDI' in string:
            return 'CDI'
        elif 'IPC-A' in string:
            return 'IPCA'
        else:
            return 'PRE'

    @property
    def tipo(self):
        string = self.string.upper()
        if 'CDB' in string:
            return 'CDB'
        elif 'LCA' in string:
            return 'LCA'
        elif 'LCI' in string:
            return 'LCI'

    @property
    def ativo(self):
        string = f' {self.string} '
        for palavra in ['FRACIONARIO', 'ED', 'ER', 'CI', '#', 'EJ', 'N1', 'S', 'NM', 'N2', 'EDR', 'ES',
                        'EB', 'EDJ', 'DRN', 'INC', 'D', 'EC', 'CORP', 'S.A.', 'S/A', 'SA',
                        'BP']:
            string = string.replace(f' {palavra} ', ' ')
        string = string.strip()
        try:
            return dicionario_ativos[string]
        except KeyError:
            print(string)


class LeitorRFGenial:

    @staticmethod
    def ler_nota(texto: list[str], df: pd.DataFrame):
        data_nota = datetime.strptime(texto[3].split(' ')[-1], '%d/%m/%Y')
        venda = 'RESGATE' in texto[4]
        identificador = texto[15].split(' ')[-7]

        if venda:
            df.loc[identificador, 'dt_venda'] = data_nota

        else:
            numero_ativo = len(df[df.index == identificador])

            try:
                taxa = TxtPDF(string=texto[18].split(' ')[3].replace("%", '')).num / 100
            except ValueError:
                taxa = TxtPDF(string=texto[18].split(' ')[-2].replace("%", '')).num / 100

            df_ = pd.DataFrame(columns=['emissor', 'tipo', 'montante', 'taxa', 'indexador', 'dt_compra',
                                        'dt_vencimento', 'dt_venda'])
            df_.loc[identificador, 'emissor'] = TxtPDF(texto[17]).emissor
            df_.loc[identificador, 'taxa'] = taxa
            df_.loc[identificador, 'indexador'] = TxtPDF(texto[18]).indexador
            df_.loc[identificador, 'tipo'] = TxtPDF(texto[15]).tipo
            df_.loc[identificador, 'dt_compra'] = data_nota
            df_.loc[identificador, 'dt_vencimento'] = datetime.strptime(texto[21].split(' ')[1], '%d/%m/%Y')
            df_.loc[identificador, 'montante'] = TxtPDF(texto[21].split(' ')[-1]).num
            df_.loc[identificador, 'numero'] = numero_ativo

            df = (df_.copy() if df.empty else pd.concat([df, df_]))

        return df

    def criar_df(self, cliente: str) -> pd.DataFrame:
        df_rf = pd.DataFrame(columns=['emissor', 'tipo', 'montante', 'taxa', 'indexador', 'dt_compra',
                                      'dt_vencimento', 'dt_venda', 'numero'])
        docs = [doc for doc in os.listdir(rf"{_caminho_notas_rf}\{cliente}") if 'Bovespa_Balcao' in doc]
        datas = [datetime.strptime(doc[15:-19], "%d-%m-%Y") for doc in docs]
        docs = pd.Series(docs, index=datas)
        docs = docs.sort_index()
        for loc in docs.index:
            with pdfplumber.open(rf"{_caminho_notas_rf}\{cliente}\{docs.loc[loc]}") as pdf:
                for pagina in pdf.pages:
                    texto = pagina.extract_text().split('\n')
                    df_rf = self.ler_nota(texto, df=df_rf)

        return df_rf

    def criar_excel(self, cliente: str):
        df = self.criar_df(cliente=cliente)
        if df.shape[0] < pd.read_excel(rf'{_caminho_rf_exportacao}\{cliente}.xlsx', index_col=0).shape[0]:
            print(f'A planilha de RF do {cliente} está diminuindo e essa função não deixou isso acontecer. ')
            return
        df.to_excel(rf'{_caminho_rf_exportacao}\{cliente}.xlsx')


class LeitorBolsa:

    @staticmethod
    def ler_nota(texto: list[str]):
        data = datetime.strptime(texto[2].split(' ')[-1], '%d/%m/%Y')
        transacoes = [i for i in texto if 'BOVESPA' in i]
        df = pd.DataFrame(columns=['data', 'natureza', 'quantidade', 'preco', 'volume', 'ativo'],
                          index=[i for i in range(len(transacoes))])
        for j, texto in enumerate(transacoes):
            palavras = texto[:-1].strip().split(' ')
            df.loc[j, 'data'] = data
            df.loc[j, 'natureza'] = palavras[1]
            df.loc[j, 'quantidade'] = TxtPDF(palavras[-3]).num
            df.loc[j, 'preco'] = TxtPDF(palavras[-2]).num
            df.loc[j, 'volume'] = TxtPDF(palavras[-1]).num
            df.loc[j, 'ativo'] = TxtPDF(' '.join(palavras[3:-3])).ativo
        return df

    def criar_df(self, cliente: str) -> pd.DataFrame:
        dfs = []
        docs = [doc for doc in os.listdir(rf"{_caminho_notas_bolsa}\{cliente}")]
        datas = [datetime.strptime(doc[-12:-4], "%d-%m-%y") for doc in docs]
        docs = pd.Series(docs, index=datas)
        docs = docs.sort_index()
        for loc in docs.index:
            with pdfplumber.open(rf"{_caminho_notas_bolsa}\{cliente}\{docs.loc[loc]}") as pdf:
                for pagina in pdf.pages:
                    texto = pagina.extract_text().split('\n')
                    dfs.append(self.ler_nota(texto))
        return pd.concat(dfs).reset_index(drop=True)

    def criar_excel(self, cliente: str):
        try:
            df = pd.read_excel(rf'{_caminho_bolsa_exportacao}\{cliente}.xlsx', index_col=0)
            df_adicional = self.criar_df(cliente=cliente)
            df_adicional = df_adicional[df_adicional.data > df.data.max()]
            if df_adicional.empty:
                df_final = df
            else:
                df_final = pd.concat([df, df_adicional])
            df_final.to_excel(rf'{_caminho_bolsa_exportacao}\{cliente}.xlsx')
        except FileNotFoundError:
            self.criar_df(cliente=cliente).to_excel(rf'{_caminho_bolsa_exportacao}\{cliente}.xlsx')


if __name__ == "__main__":
    LeitorRFGenial().criar_excel(cliente='Larissa Lopes')
