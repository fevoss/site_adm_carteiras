
import streamlit as st

# Variáveis de Sessão
if 'logado' not in st.session_state:
    st.session_state['logado'] = False

if 'admin' not in st.session_state:
    st.session_state['admin'] = None

# Páginas
login = st.Page(
    page="pages/visitante/login.py",
    title="Entrar",
    icon=":material/login:",
    default=not st.session_state['logado']
)

signup = st.Page(
    page="pages/visitante/sign_up.py",
    title="Cadastre-se",
    icon=":material/person_add:"
)
#
sobre_nos = st.Page(
    page="pages/visitante/sobre_nos.py",
    title="Sobre Nós",
    icon=":material/person:"
)

logout = st.Page(
    page="pages/logado/logout.py",
    title="Sair",
    icon=":material/logout:"
)

resumo = st.Page(
    page="pages/logado/resumo.py",
    title="Resumo",
    icon=":material/account_balance_wallet:",
    default=st.session_state['logado']
)

performance = st.Page(
    page="pages/admin/performance.py",
    title="Performance",
    icon=":material/account_balance:",
    default=st.session_state['logado']
)


not_logged_in = [login, signup, sobre_nos]
logged_in = [resumo, logout]
admin = [performance, logout]

# Barra de navegação
if not st.session_state['logado']:
    pg = st.navigation(not_logged_in)
elif st.session_state['admin']:
    pg = st.navigation(admin)
else:
    pg = st.navigation(logged_in)

st.logo("assets/logo.png")
st.sidebar.text("Made by Fevos")
# Run Navigation
pg.run()

# st.write(st.session_state)

