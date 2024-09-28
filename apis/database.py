import sqlite3
from sqlite3 import Error
import hashlib
from pathlib import Path


class Database:

    def __init__(self, database: str):
        self.database = f'{Path(__file__).resolve().parent.parent}/database/{database}.db'
        self.con = None

    def __enter__(self):
        """ Abre a conexão com o banco de dados """
        try:
            self.con = sqlite3.connect(self.database)
            print(f"Conexão estabelecida com {self.database}")
            return self.con
        except Error as e:
            print(f"Erro ao conectar ao banco de dados: {e}")
            raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        """ Fecha a conexão ao sair do contexto """
        if self.con:
            self.con.close()
            print(f"Conexão com {self.database} encerrada")
        # Repassa exceções se existirem
        if exc_type:
            print(f"Exceção: {exc_type}, {exc_val}")
        return False  # Re-raise exceptions if any


class Usuarios:

    def __init__(self):
        self.database = 'clientes'

    def _criar_dim_usuario(self):
        """ Cria a tabela usuario no banco de dados """
        with Database(self.database) as con:
            sql = """
            CREATE TABLE IF NOT EXISTS usuario (
                usuario_id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                cpf INT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                senha TEXT NOT NULL,
                flg_admin INT NOT NULL DEFAULT 0
            );"""

            try:
                c = con.cursor()
                c.execute(sql)
                print("Tabela usuario criada com sucesso!")
            except Error as e:
                print(e)

    @staticmethod
    def _criptografar_senha(senha: any):
        valor_bytes = senha.encode()  # Converte a string em bytes
        hash_obj = hashlib.sha256(valor_bytes)  # Cria o objeto hash
        hash_valor = hash_obj.hexdigest()  # Retorna o hash em formato hexadecimal
        return hash_valor

    def adicionar_usuario(self, nome, email, senha, cpf):
        self._criar_dim_usuario()
        senha = self._criptografar_senha(senha)
        with Database(self.database) as con:
            sql = '''INSERT INTO usuario(nome, email, senha, cpf)
                     VALUES(?,?,?, ?)'''
            cur = con.cursor()
            cur.execute(sql, (nome, email, senha, cpf))
            con.commit()

    def autenticar(self, cpf: str, senha):
        with Database(self.database) as con:
            sql = '''
            SELECT senha FROM usuario where cpf = (?)
            LIMIT 1
            '''
            cur = con.cursor()
            cur.execute(sql, (cpf,))
            row = cur.fetchone()
            return row[0] == self._criptografar_senha(senha)

    def acesso_administrador(self, cpf: str) -> bool:
        with Database(self.database) as con:
            sql = '''
            SELECT flg_admin FROM usuario where cpf = (?)
            LIMIT 1
            '''
            cur = con.cursor()
            cur.execute(sql, (cpf,))
            row = cur.fetchone()
            return bool(row[0])

    def obter_base(self):
        """ Coleta todos os usuários da tabela usuario """
        with Database(self.database) as con:
            try:
                cur = con.cursor()
                cur.execute("SELECT * FROM usuario")  # Consulta para coletar todos os registros
                rows = cur.fetchall()  # Coleta todos os resultados
                return rows
            except Error as e:
                print(e)
                return None

    def conceder_acesso_admin(self, cpf: str):
        with Database(self.database) as con:
            sql = '''
            UPDATE usuario
            SET flg_admin = 1 
            WHERE cpf = ?
            '''
            cur = con.cursor()
            cur.execute(sql, (cpf, ))
            con.commit()


class MarketData:

    def __init__(self):
        self.database = 'market_data'

    def criar_tabelas_market_data(self):

        with Database(self.database) as con:
            # Tabela de Ações
            dim_ticker = """
            CREATE TABLE IF NOT EXISTS acao (
                acao_id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL UNIQUE,
                nome_empresa TEXT NOT NULL
            );"""

            # Tabela de Cotações de Ações
            fat_cotacoes = """
            CREATE TABLE IF NOT EXISTS precos (
                acao_id INTEGER NOT NULL,
                data DATE NOT NULL,
                cotacao REAL NOT NULL,
                FOREIGN KEY (acao_id) REFERENCES acao (acao_id)
            );"""

            try:
                c = con.cursor()
                c.execute(dim_ticker)
                c.execute(fat_cotacoes)
                print("Tabela usuario criada com sucesso!")
            except Error as e:
                print(e)


if __name__ == "__main__":
    print(Usuarios().conceder_acesso_admin("50042397898"))
    print(Usuarios().obter_base())
