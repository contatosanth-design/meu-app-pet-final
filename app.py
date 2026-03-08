import streamlit as st

st.set_page_config(
    page_title="Sistema Veterinário",
    page_icon="🐾",
    layout="centered"
)

st.title("🐾 Sistema Veterinário")

st.write("Sistema online funcionando no Render.")

nome = st.text_input("Nome do tutor")
pet = st.text_input("Nome do pet")
idade = st.number_input("Idade do pet", min_value=0, max_value=50)

if st.button("Registrar atendimento"):
    st.success(f"Atendimento registrado para {pet} (Tutor: {nome})")
