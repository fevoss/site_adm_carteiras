import streamlit as st

col1, col2 = st.columns(2, gap="small", vertical_alignment="center")

with col1:
    st.image("./assets/perfil.png")

with col2:
    st.title("Felipe Lima", anchor=False)
    st.text("""
             O Fevos será um futuro administrador
             de carteiras\n
             Formação:\n
                • Graduado em Economia pelo INSPER\n
                • Certificado com CPA-20 e CFG
            
             O que eu mais quero é poder ser livre
             """)