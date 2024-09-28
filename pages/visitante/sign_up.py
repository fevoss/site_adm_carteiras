import time

import streamlit as st
from apis.database import Usuarios
import sqlite3

st.title("Cadastre-se")
form_cadastro = st.form(key="signup-form")
with form_cadastro:
    nome = st.text_input("Nome")
    email = st.text_input("Email")
    cpf = st.text_input("CPF")
    senha = st.text_input("Senha", type='password')
    botao = st.form_submit_button("Cadastrar")

    if botao:
        try:
            Usuarios().adicionar_usuario(nome, email, senha, cpf)
            st.success(f"{nome}, você foi cadastrado com sucesso!")
            time.sleep(3)
            st.switch_page("pages/visitante/login.py")
        except sqlite3.IntegrityError:
            st.error("Usuário já foi cadastrado")
