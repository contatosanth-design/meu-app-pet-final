import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. CONFIGURAÇÃO DE DESIGN PROFISSIONAL
st.set_page_config(page_title="Ribeira Vet Pro v18", layout="wide", page_icon="🐾")

st.markdown("""
    <style>
    /* Estilo Minimalista e Limpo */
    .stApp { background-color: #F8FAFC !important; color: #1E293B !important; }
    
    /* Sidebar Elegante */
    [data-testid="stSidebar"] { background-color: #0F172A !important; color: white !important; }
    [data-testid="stSidebar"] * { color: white !important; }
    
    /* Logo 40x40 no topo */
    .sidebar-logo { display: flex; justify-content: center; margin-bottom: 20px; }
    .stImage > img { width: 40px !important; height: 40px !important; border-radius: 8px; }

    /* BOTÃO AMARELO - LIMPO E LEVÍVEL */
    button, .stButton>button {
        background-color: #FFD700 !important; 
        color: #000000 !important; 
        font-weight: bold !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 10px 20px !important;
        transition: 0.3s !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
    }
    button:hover { background-color: #FACC15 !important; transform: translateY(-2px); }

    /* Cards do Painel */
    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        border-left: 5px solid #FFD700;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        text-align: center;
    }
    
    /* Inputs Brancos com Borda Suave */
    input, textarea, select { 
        background-color: white !important; 
        color: black !important; 
        border-radius: 8px !important;
        border: 1px solid #E2E8F0 !important; 
    }
    </style>
    """, unsafe_allow_html=True)

# 2. SISTEMA DE ARQUIVOS
def carregar(arq, cols):
    if os.path.exists(arq): return pd.read_csv(arq)
    return pd.DataFrame(columns=cols)

if 't_db' not in st.session_state: st.session_state.t_db = carregar('t_v18.csv', ["CPF", "Nome", "Whats"])
if 'p_db' not in st.session_state: st.session_state.p_db = carregar('p_v18.csv', ["Dono", "Pet", "Tipo"])
if 'c_db' not in st.session_state: st.session_state.c_db = carregar('c_v18.csv', ["Data", "Pet", "Relato"])

# 3. MENU LATERAL
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2138/2138440.png") # Seu logo 40x40
    st.markdown("### Ribeira Vet Pro")
    st.write("---")
    menu = st.radio("Navegação", ["📊 Dashboard", "👤 Clientes", "🐾 Pets", "⚕️ Atendimento", "💰 Financeiro"])
    st.write("---")
    st.caption("Versão 18.0 - Interface Limpa")

# 4. ÁREAS DE CONTEÚDO

if menu == "📊 Dashboard":
    st.title("📊 Visão Geral")
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown(f'<div class="metric-card"><h3>Clientes</h3><h2>{len(st.session_state.t_db)}</h2></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="metric-card"><h3>Pets</h3><h2>{len(st.session_state.p_db)}</h2></div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="metric-card"><h3>Consultas</h3><h2>{len(st.session_state.c_db)}</h2></div>', unsafe_allow_html=True)
    
    st.subheader("📋 Últimos Atendimentos")
    st.dataframe(st.session_state.c_db.tail(5), use_container_width=True)

elif menu == "👤 Clientes":
    st.title("👤 Gestão de Clientes")
    with st.form("add_tutor"):
        n = st.text_input("Nome Completo")
        c = st.text_input("CPF")
        w = st.text_input("WhatsApp")
        if st.form_submit_button("CADASTRAR"):
            novo = pd.DataFrame([{"CPF": c, "Nome": n, "Whats": w}])
            st.session_state.t_db = pd.concat([st.session_state.t_db, novo], ignore_index=True)
            st.session_state.t_db.to_csv('t_v18.csv', index=False)
            st.success("Tutor salvo!")

elif menu == "🐾 Pets":
    st.title("🐾 Cadastro de Animais")
    if st.session_state.t_db.empty: st.info("Cadastre um cliente primeiro.")
    else:
        with st.form("add_pet"):
            d = st.selectbox("Dono", st.session_state.t_db['Nome'])
            p = st.text_input("Nome do Pet")
            t = st.selectbox("Espécie", ["Canina", "Felina", "Outra"])
            if st.form_submit_button("SALVAR PET"):
                novo_p = pd.DataFrame([{"Dono": d, "Pet": p, "Tipo": t}])
                st.session_state.p_db = pd.concat([st.session_state.p_db, novo_p], ignore_index=True)
                st.session_state.p_db.to_csv('p_v18.csv', index=False)
                st.success(f"{p} cadastrado!")

elif menu == "⚕️ Atendimento":
    st.title("⚕️ Prontuário Médico")
    if st.session_state.p_db.empty: st.info("Nenhum pet cadastrado.")
    else:
        with st.form("consulta"):
            sel_p = st.selectbox("Paciente", st.session_state.p_db['Pet'])
            txt = st.text_area("Anamnese e Prescrição", height=200)
            if st.form_submit_button("FINALIZAR CONSULTA"):
                data = datetime.now().strftime("%d/%m/%Y")
                novo_c = pd.DataFrame([{"Data": data, "Pet": sel_p, "Relato": txt}])
                st.session_state.c_db = pd.concat([st.session_state.c_db, novo_c], ignore_index=True)
                st.session_state.c_db.to_csv('c_v18.csv', index=False)
                st.success("Gravado no histórico!")

elif menu == "💰 Financeiro":
    st.title("💰 Tabelas de Preços")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Serviços")
        st.table({"Item": ["Consulta", "Vax V10", "Castração"], "Preço": ["R$150", "R$120", "R$450"]})
    with c2:
        st.subheader("Farmácia")
        st.table({"Item": ["Vermífugo", "Antibiótico", "Shampoo"], "Preço": ["R$45", "R$65", "R$80"]})
