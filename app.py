import streamlit as st
import pandas as pd
from datetime import datetime
import os

# 1. CONFIGURAÇÃO DA PÁGINA (MODO AMPLO)
st.set_page_config(page_title="Ribeira Vet Pro", layout="wide", page_icon="🐾")

# 2. ESTILO CSS PARA PARECER SOFTWARE PROFISSIONAL
st.markdown("""
    <style>
    /* Fundo e Fontes */
    .stApp { background-color: #f4f7f6; }
    html, body, [class*="css"] { font-size: 0.85rem !important; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    
    /* Cartões de Métricas (Dashboard) */
    .metric-card {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #2E7D32;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
        text-align: center;
    }
    .card-red { border-left-color: #d32f2f; }
    .card-orange { border-left-color: #f57c00; }
    .card-blue { border-left-color: #1976d2; }
    
    /* Ajuste de tabelas */
    .stDataFrame { border: 1px solid #e0e0e0; border-radius: 10px; background-color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- BANCO DE DADOS ---
def carregar_dados():
    if os.path.exists('responsaveis.csv'):
        return pd.read_csv('responsaveis.csv')
    return pd.DataFrame(columns=["ID", "Nome", "CPF", "Endereço", "Animais", "Status"])

if 'dados' not in st.session_state:
    st.session_state.dados = carregar_dados()

# --- BARRA LATERAL (MENU) ---
with st.sidebar:
    st.markdown("## 🏥 Ribeira Vet")
    st.image("https://cdn-icons-png.flaticon.com/512/2138/2138440.png", width=80)
    menu = st.selectbox("Menu Principal", ["📊 Painel Geral", "📝 Cadastros", "📋 Prontuários", "💰 Financeiro"])
    st.divider()
    st.caption("Versão 7.0 Alpha - 2026")

# --- CONTEÚDO PRINCIPAL ---

if menu == "📊 Painel Geral":
    st.markdown("### 📈 Visão Geral do Consultório")
    
    # CRIANDO OS CARDS COLORIDOS IGUAL AO SEU EXEMPLO
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        st.markdown('<div class="metric-card card-red"><strong>Vencidos</strong><br><h2 style="color:#d32f2f; margin:0;">15</h2></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="metric-card card-orange"><strong>Pendentes</strong><br><h2 style="color:#f57c00; margin:0;">08</h2></div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="metric-card card-blue"><strong>Consultas Hoje</strong><br><h2 style="color:#1976d2; margin:0;">12</h2></div>', unsafe_allow_html=True)
    with c4:
        st.markdown('<div class="metric-card"><strong>Total Clientes</strong><br><h2 style="color:#2E7D32; margin:0;">'+str(len(st.session_state.dados))+'</h2></div>', unsafe_allow_html=True)

    st.divider()
    
    # LISTA DE PRODUTOS/SERVIÇOS (TABELA COMPLETA)
    st.markdown("#### 🔍 Lista de Pacientes e Responsáveis")
    
    # Usando o data_editor para ser "clicável" e "editável" como você pediu
    eventos = st.data_editor(
        st.session_state.dados,
        use_container_width=True,
        num_rows="dynamic",
        column_config={
            "Status": st.column_config.SelectboxColumn("Situação", options=["Ativo", "Inativo", "Pendente"], required=True),
            "CPF": st.column_config.TextColumn("Documento CPF"),
        }
    )
    
    if st.button("💾 Salvar Alterações no Sistema"):
        st.session_state.dados = eventos
        eventos.to_csv('responsaveis.csv', index=False)
        st.success("Dados sincronizados com sucesso!")

elif menu == "📝 Cadastros":
    st.subheader("🆕 Novo Registro de Responsável")
    with st.container(border=True):
        col_a, col_b = st.columns(2)
        with col_a:
            nome = st.text_input("Nome do Tutor")
            cpf = st.text_input("CPF")
        with col_b:
            end = st.text_area("Endereço Completo", height=68)
        
        animais = st.text_input("Animais (Ex: Totó - Golden, Mimi - Persa)")
        
        if st.button("Finalizar Cadastro"):
            # Lógica de salvar...
            st.balloons()
