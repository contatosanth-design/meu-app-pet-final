import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Configuração da Página (Visual Moderno)
st.set_page_config(page_title="Ribeira Vet Pro", layout="wide", page_icon="🐾")

# --- BANCO DE DADOS SIMULADO (LOCAL E NUVEM) ---
# Em um cenário real, aqui conectaríamos ao Firebase
def carregar_dados(arquivo):
    if os.path.exists(arquivo):
        return pd.read_csv(arquivo)
    return pd.DataFrame()

# Inicialização do Estado da Sessão
if 'dados_responsaveis' not in st.session_state:
    st.session_state.dados_responsaveis = carregar_dados('responsaveis.csv')

# --- INTERFACE ---
st.title("🛡️ Sistema de Gestão Veterinária - Ribeira Vet Pro")

menu = st.sidebar.selectbox("Navegação", ["Cadastrar Responsável", "Lista de Responsáveis", "Prontuários"])

if menu == "Cadastrar Responsável":
    st.header("📝 Cadastro de Responsável (Ex-Tutor)")
    
    with st.form("form_cadastro"):
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome Completo")
            cpf = st.text_input("CPF (Somente números)")
            id_cadastro = st.text_input("Número de Registro/ID", value=datetime.now().strftime("%Y%m%d%H%M"))
        with col2:
            endereco = st.text_area("Endereço Completo (Rua, Nº, Bairro, CEP)")
            contato = st.text_input("Telefone de Contato")
        
        animais = st.text_area("Animais (Nome, Espécie, Raça - separados por vírgula)")
        
        enviar = st.form_submit_button("Salvar Cadastro")
        
        if enviar:
            novo_dado = {
                "ID": id_cadastro, "Nome": nome, "CPF": cpf, 
                "Endereço": endereco, "Animais": animais, "Data": datetime.now()
            }
            # Adicionando ao DataFrame
            st.session_state.dados_responsaveis = pd.concat([st.session_state.dados_responsaveis, pd.DataFrame([novo_dado])], ignore_index=True)
            # Salvar Localmente (Backup)
            st.session_state.dados_responsaveis.to_csv('responsaveis.csv', index=False)
            st.success("Dados salvos com sucesso na nuvem e localmente!")

elif menu == "Lista de Responsáveis":
    st.header("👥 Gerenciamento de Dados")
    st.info("Clique nas células abaixo para editar os dados diretamente. As alterações são salvas automaticamente.")
    
    # Lista Clicável e Editável
    df_editavel = st.data_editor(
        st.session_state.dados_responsaveis,
        column_config={
            "ID": st.column_config.TextColumn("Registro nº", disabled=True),
            "CPF": st.column_config.TextColumn("CPF"),
            "Animais": st.column_config.ListColumn("Pets Vinculados")
        },
        num_rows="dynamic",
        use_container_width=True
    )
    
    if st.button("Confirmar Alterações na Nuvem"):
        st.session_state.dados_responsaveis = df_editavel
        df_editavel.to_csv('responsaveis.csv', index=False)
        st.balloons()

elif menu == "Prontuários":
    st.header("📋 Acesso Imediato ao Prontuário")
    busca = st.selectbox("Selecione o Responsável para ver o Prontuário", st.session_state.dados_responsaveis["Nome"].unique() if not st.session_state.dados_responsaveis.empty else [])
    
    if busca:
        dados = st.session_state.dados_responsaveis[st.session_state.dados_responsaveis["Nome"] == busca]
        st.subheader(f"Ficha Médica: {busca}")
        st.write(f"**CPF:** {dados['CPF'].values[0]} | **ID:** {dados['ID'].values[0]}")
        st.write(f"**Endereço:** {dados['Endereço'].values[0]}")
        st.divider()
        st.text_area("Evolução Clínica / Prontuário", height=300, placeholder="Digite aqui as informações da consulta conforme a legislação...")
        st.button("Salvar Prontuário Digital")
