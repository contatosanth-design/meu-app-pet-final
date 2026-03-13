import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. CONFIGURAÇÃO DE TELA E LOGO
st.set_page_config(page_title="Ribeira Vet Pro v15", layout="wide", page_icon="🏥")

st.markdown("""
    <style>
    /* Forçar Fundo Branco e Texto Escuro */
    .stApp { background-color: white !important; color: #1E293B !important; }
    
    /* --- LOGOTIPO 40x40 --- */
    [data-testid="stSidebarNav"] { background-image: none; }
    .stImage > img { width: 40px !important; height: 40px !important; border-radius: 5px; }

    /* --- O BOTÃO AGORA É AMARELO DE VERDADE --- */
    button[kind="primary"], .stButton > button {
        background-color: #FFD700 !important; 
        color: #000000 !important; 
        font-weight: bold !important;
        border: 2px solid #B8860B !important;
        width: 100% !important;
        height: 3.5em !important;
    }

    /* --- CURSOR PRETO E CAMPOS CLAROS --- */
    input, textarea, select { 
        background-color: #F8FAFC !important; 
        color: black !important; 
        caret-color: black !important; 
        border: 1px solid #CBD5E1 !important; 
    }
    label { color: #1E293B !important; font-weight: bold !important; }

    /* CARDS COLORIDOS */
    .card { padding: 20px; border-radius: 12px; color: white !important; text-align: center; font-weight: bold; }
    .vencido { background-color: #EF4444; } 
    .pendente { background-color: #F59E0B; } 
    .hoje { background-color: #3B82F6; } 
    .total { background-color: #10B981; }
    </style>
    """, unsafe_allow_html=True)

# 2. BANCO DE DADOS UNIFICADO
def carregar(nome, cols):
    if os.path.exists(nome): return pd.read_csv(nome)
    return pd.DataFrame(columns=cols)

if 'df_tutores' not in st.session_state:
    st.session_state.df_tutores = carregar('tutores_v15.csv', ["CPF", "Tutor", "WhatsApp", "Endereço"])
if 'df_pets' not in st.session_state:
    st.session_state.df_pets = carregar('pets_v15.csv', ["CPF_Tutor", "Pet", "Espécie", "Raça", "Idade", "Peso"])

# 3. MENU LATERAL
with st.sidebar:
    # URL da sua imagem (substitua pelo seu link se desejar)
    st.image("https://cdn-icons-png.flaticon.com/512/2138/2138440.png")
    st.markdown("### Ribeira Vet Pro")
    st.info("📍 **VERSÃO 15.0 - COMPLETA**")
    menu = st.radio("Navegação:", ["📊 Painel Geral", "👤 Novo Tutor", "🐾 Novo Animal", "⚕️ Consultório"])

# 4. PÁGINAS ATIVAS

if menu == "📊 Painel Geral":
    st.markdown("### 📊 Status da Clínica")
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown('<div class="card vencido">Vencidos<br><h2>15</h2></div>', unsafe_allow_html=True)
    with c2: st.markdown('<div class="card pendente">Pendentes<br><h2>08</h2></div>', unsafe_allow_html=True)
    with c3: st.markdown('<div class="card hoje">Consultas Hoje<br><h2>12</h2></div>', unsafe_allow_html=True)
    with c4: st.markdown(f'<div class="card total">Pets Ativos<br><h2>{len(st.session_state.df_pets)}</h2></div>', unsafe_allow_html=True)
    st.divider()
    st.subheader("👥 Tutores Cadastrados")
    st.dataframe(st.session_state.df_tutores, use_container_width=True)

elif menu == "👤 Novo Tutor":
    st.subheader("👤 Cadastro de Proprietário")
    with st.form("tutor_v15"):
        c1, c2 = st.columns(2)
        nome = c1.text_input("Nome Completo")
        cpf = c2.text_input("CPF")
        c3, c4 = st.columns([1, 2])
        whats = c3.text_input("WhatsApp")
        end = c4.text_input("Endereço Completo")
        if st.form_submit_button("SALVAR TUTOR"):
            if nome and cpf:
                novo = pd.DataFrame([{"CPF": cpf, "Tutor": nome, "WhatsApp": whats, "Endereço": end}])
                st.session_state.df_tutores = pd.concat([st.session_state.df_tutores, novo], ignore_index=True)
                st.session_state.df_tutores.to_csv('tutores_v15.csv', index=False)
                st.success("Tutor salvo com sucesso!")

elif menu == "🐾 Novo Animal":
    st.subheader("🐾 Cadastrar Pet")
    if st.session_state.df_tutores.empty:
        st.warning("⚠️ Cadastre um tutor antes.")
    else:
        with st.form("pet_v15"):
            tutor_ref = st.selectbox("Dono:", st.session_state.df_tutores['Tutor'] + " (" + st.session_state.df_tutores['CPF'] + ")")
            cpf_vinculo = tutor_ref.split("(")[-1].replace(")", "")
            c1, c2, c3 = st.columns(3)
            nome_p = c1.text_input("Nome do Pet")
            especie = c2.selectbox("Espécie", ["Canina", "Felina", "Outra"])
            raca = c3.text_input("Raça")
            if st.form_submit_button("CADASTRAR ANIMAL"):
                novo_p = pd.DataFrame([{"CPF_Tutor": cpf_vinculo, "Pet": nome_p, "Espécie": especie, "Raça": raca}])
                st.session_state.df_pets = pd.concat([st.session_state.df_pets, novo_p], ignore_index=True)
                st.session_state.df_pets.to_csv('pets_v15.csv', index=False)
                st.success(f"{nome_p} cadastrado!")

elif menu == "⚕️ Consultório":
    st.subheader("⚕️ Atendimento")
    st.info("Pronto para iniciar a consulta.")
