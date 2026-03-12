import streamlit as st
import pandas as pd
import os

# Configuração Básica
st.set_page_config(page_title="Ribeira Vet Pro", layout="wide")

# Banco de Dados Simples
if 'dados' not in st.session_state:
    if os.path.exists('responsaveis.csv'):
        st.session_state.dados = pd.read_csv('responsaveis.csv')
    else:
        st.session_state.dados = pd.DataFrame(columns=["ID", "Nome", "CPF", "Status"])

# Título Principal
st.title("🏥 Ribeira Vet Pro - Painel de Gestão")

# Dashboard de Métricas (Sem CSS complexo para evitar erro)
c1, c2, c3 = st.columns(3)
c1.metric("Vencidos", "15", delta="-2", delta_color="inverse")
c2.metric("Consultas Hoje", "12")
c3.metric("Total Clientes", len(st.session_state.dados))

st.divider()

# Menu e Tabela
menu = st.sidebar.radio("Navegação", ["Painel", "Cadastros"])

if menu == "Painel":
    st.subheader("🔍 Lista de Registros")
    df_editado = st.data_editor(st.session_state.dados, use_container_width=True)
    if st.button("Salvar Alterações"):
        df_editado.to_csv('responsaveis.csv', index=False)
        st.success("Sincronizado!")
else:
    st.write("Área de Cadastro")
