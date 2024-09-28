import time

import streamlit as st
from apis.database import Usuarios


st.title("Login")

with st.form(key="login"):
    cpf = st.text_input("CPF")
    senha = st.text_input("Senha", type='password')
    botao = st.form_submit_button("Login")

    if botao:
        try:
            if Usuarios().autenticar(cpf, senha):
                st.success("Login Efetuado com Sucesso")
                st.session_state['logado'] = True
                st.session_state['admin'] = Usuarios().acesso_administrador(cpf=cpf)
                time.sleep(1)
                st.rerun()

            else:
                st.error("Senha está incorreta")
        except TypeError:
            st.error("CPF inválido")
