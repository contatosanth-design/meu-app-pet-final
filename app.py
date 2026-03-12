import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. TRAVA DE INTERFACE (VERSÃO 10.0 - VERIFICAÇÃO VISUAL)
st.set_page_config(page_title="Ribeira Vet Pro v10", layout="wide", page_icon="🏥")

st.markdown("""
    <style>
    /* Forçar Fundo Branco para ignorar modo escuro do navegador */
    .stApp { background-color: #FFFFFF !important; color: #1E293B !important; }
    
    /* BOTÃO FINALIZAR AMARELO (Conforme solicitado) */
    div.stButton > button:first-child {
        background-color: #FFD700 !important; /* Amarelo Ouro */
        color: #000000 !important;
        font-weight: bold !important;
        border: 2px solid #B8860B !important;
        width: 100% !important;
        height: 3.5em !important;
    }

    /* Estilo dos Cards do Dashboard */
    .card {
        padding: 20px; border-radius: 12px; color: white !important;
        text-align: center; font-weight: bold; box-shadow: 2px 4px 8px rgba(0,0,0,0.1);
    }
    .vencido { background-color: #EF4444; } 
    .pendente { background-color: #F59E0B; } 
    .hoje { background-color: #3B82F6; } 
    .total { background-color: #10B981; }

    /* Inputs Visíveis */
    input, textarea, select { 
        background-color: #F9FAFB !important; 
        color: black !important; 
        border: 1px solid #D1D5DB !important; 
    }
    </style>
    """, unsafe_allow_html=True)

# 2. BANCO DE DADOS ATUALIZADO (v10)
def carregar_dados():
    arquivo = 'banco_ribeira_v10.csv'
    if os.path.exists(arquivo):
        return pd.read_csv(arquivo)
    return pd.DataFrame(columns=[
        "ID", "Tutor", "CPF", "WhatsApp", "Endereço", 
        "Nome Pet", "Espécie", "Raça", "Idade", "Peso", "Sexo", "Histórico"
    ])

if 'dados' not in st.session_state:
    st.session_state.dados = carregar_dados()

# 3. BARRA LATERAL
with st.sidebar:
    st.markdown("### 🏥 Ribeira Vet Pro")
    st.info("📌 **VERSÃO 10.0** (Atualizado)")
    menu = st.radio("Menu Principal", ["📊 Painel Geral", "📝 Ficha de Atendimento", "⚕️ Prontuário e IA"])
    st.divider()
    csv = st.session_state.dados.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Backup Completo (Excel)", data=csv, file_name="backup_v10.csv")

# 4. PÁGINAS

if menu == "📊 Painel Geral":
    st.markdown("### 📊 Indicadores da Clínica")
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown('<div class="card vencido">Vencidos<br><h2>15</h2></div>', unsafe_allow_html=True)
    with c2: st.markdown('<div class="card pendente">Pendentes<br><h2>08</h2></div>', unsafe_allow_html=True)
    with c3: st.markdown('<div class="card hoje">Consultas Hoje<br><h2>12</h2></div>', unsafe_allow_html=True)
    with c4: st.markdown('<div class="card total">Clientes Ativos<br><h2>'+str(len(st.session_state.dados))+'</h2></div>', unsafe_allow_html=True)
    
    st.divider()
    st.markdown("#### 🔍 Base de Dados Completa")
    st.data_editor(st.session_state.dados, use_container_width=True, hide_index=True)

elif menu == "📝 Ficha de Atendimento":
    st.markdown("### 📝 Cadastro Completo (Tutor e Animal)")
    
    with st.form("ficha_v10", clear_on_submit=True):
        st.markdown("#### 👤 1. Dados do Tutor")
        col_t1, col_t2 = st.columns([2, 1])
        tutor_nome = col_t1.text_input("Nome do Tutor (Responsável)")
        tutor_cpf = col_t2.text_input("CPF")
        
        col_t3, col_t4 = st.columns([1, 2])
        tutor_whats = col_t3.text_input("WhatsApp")
        tutor_end = col_t4.text_input("Endereço Completo (Rua, Bairro, Cidade)")
        
        st.divider()
        st.markdown("#### 🐾 2. Dados do Animal (Paciente)")
        col_p1, col_p2, col_p3 = st.columns(3)
        pet_nome = col_p1.text_input("Nome do Animal")
        pet_especie = col_p2.selectbox("Espécie", ["Canina", "Felina", "Exóticos", "Outros"])
        pet_raca = col_p3.text_input("Raça")
        
        col_p4, col_p5, col_p6 = st.columns(3)
        pet_idade = col_p4.text_input("Idade")
        pet_peso = col_p5.text_input("Peso (kg)")
        pet_sexo = col_p6.selectbox("Sexo", ["Macho", "Fêmea"])
        
        st.divider()
        if st.form_submit_button("CONCLUIR CADASTRO"):
            novo_id = datetime.now().strftime("%y%m%d%H%M")
            nova_linha = pd.DataFrame([{
                "ID": novo_id, "Tutor": tutor_nome, "CPF": tutor_cpf, "WhatsApp": tutor_whats, "Endereço": tutor_end,
                "Nome Pet": pet_nome, "Espécie": pet_especie, "Raça": pet_raca, 
                "Idade": pet_idade, "Peso": pet_peso, "Sexo": pet_sexo, "Histórico": "Ficha aberta"
            }])
            st.session_state.dados = pd.concat([st.session_state.dados, nova_linha], ignore_index=True)
            st.session_state.dados.to_csv('banco_ribeira_v10.csv', index=False)
            st.success(f"✅ {pet_nome} cadastrado com sucesso!")
            st.balloons()

elif menu == "⚕️ Prontuário e IA":
    st.subheader("⚕️ Evolução Clínica e IA")
    if not st.session_state.dados.empty:
        busca = st.selectbox("Selecione o Paciente:", st.session_state.dados["Nome Pet"].unique())
        st.info("Assistente de IA: Descreva os sintomas para receber uma sugestão de protocolo.")
        st.text_area("Histórico Clínico:", height=250)
    else:
        st.error("Cadastre um animal primeiro na aba de Cadastro.")
