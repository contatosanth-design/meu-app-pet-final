import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. DESIGN "SOFT CLEAN" - ALTO CONTRASTE SEM AGRESSIVIDADE
st.set_page_config(page_title="Ribeira Vet Pro v22", layout="wide")

st.markdown("""
    <style>
    /* Fundo branco e texto cinza escuro para leitura perfeita */
    .stApp { background-color: #FFFFFF !important; }
    h1, h2, h3, p, span, label { color: #1E293B !important; font-family: 'Segoe UI', sans-serif; }
    
    /* Sidebar moderna */
    [data-testid="stSidebar"] { background-color: #F8FAFC !important; border-right: 1px solid #E2E8F0; }
    
    /* Botão Amarelo Profissional */
    div.stButton > button {
        background-color: #FFD700 !important;
        color: #000000 !important;
        font-weight: bold !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 0.5rem 1rem !important;
    }
    
    /* Inputs suaves e visíveis */
    input, textarea, select { 
        background-color: #FFFFFF !important; 
        border: 1px solid #CBD5E1 !important; 
        color: #000000 !important;
        border-radius: 5px !important;
    }
    
    /* Tabelas limpas */
    .stDataFrame { border: 1px solid #E2E8F0 !important; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

# 2. CARREGAMENTO DE DADOS
def carregar(arq, cols):
    if os.path.exists(arq): return pd.read_csv(arq)
    return pd.DataFrame(columns=cols)

arq_tutores = 'tutores_v22.csv'
arq_pets = 'pets_v22.csv'

if 'df_tutores' not in st.session_state:
    st.session_state.df_tutores = carregar(arq_tutores, ["Nome", "CPF", "WhatsApp", "Email", "Endereco"])
if 'df_pets' not in st.session_state:
    st.session_state.df_pets = carregar(arq_pets, ["Dono", "Pet", "Especie", "Raca", "Peso", "Idade"])

# 3. MENU LATERAL CORRIGIDO
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2138/2138440.png", width=50)
    st.markdown("### Ribeira Vet Pro")
    st.write("---")
    # AQUI ESTAVA O ERRO: O MENU AGORA TEM NOMES CLAROS
    menu = st.radio("NAVEGAÇÃO:", ["👤 Clientes", "🐾 Animais", "💰 Financeiro", "📊 Banco de Dados"])

# 4. TELAS

if menu == "👤 Clientes":
    st.title("👤 Cadastro de Clientes")
    with st.form("form_cliente", clear_on_submit=True):
        c1, c2 = st.columns(2)
        nome = c1.text_input("Nome do Responsável")
        cpf = c2.text_input("CPF")
        whats = c1.text_input("WhatsApp")
        email = c2.text_input("E-mail")
        end = st.text_input("Endereço Completo")
        if st.form_submit_button("SALVAR CLIENTE"):
            novo = pd.DataFrame([{"Nome": nome, "CPF": cpf, "WhatsApp": whats, "Email": email, "Endereco": end}])
            st.session_state.df_tutores = pd.concat([st.session_state.df_tutores, novo], ignore_index=True)
            st.session_state.df_tutores.to_csv(arq_tutores, index=False)
            st.success("Cliente registrado!")
            st.rerun()
    st.subheader("Clientes na Base")
    st.dataframe(st.session_state.df_tutores, use_container_width=True)

elif menu == "🐾 Animais":
    st.title("🐾 Cadastro de Pets")
    with st.form("form_pet", clear_on_submit=True):
        # Seleciona o dono da lista de clientes cadastrados
        lista_donos = ["Não Informado"] + st.session_state.df_tutores['Nome'].tolist()
        dono = st.selectbox("Vincular ao Dono:", lista_donos)
        
        c1, c2 = st.columns(2)
        p_nome = c1.text_input("Nome do Pet")
        p_esp = c2.selectbox("Espécie", ["Cão", "Gato", "Ave", "Outro"])
        p_raca = c1.text_input("Raça")
        p_idade = c2.text_input("Idade")
        p_peso = c1.text_input("Peso (kg)")
        
        if st.form_submit_button("SALVAR PET"):
            novo_p = pd.DataFrame([{"Dono": dono, "Pet": p_nome, "Especie": p_esp, "Raca": p_raca, "Peso": p_peso, "Idade": p_idade}])
            st.session_state.df_pets = pd.concat([st.session_state.df_pets, novo_p], ignore_index=True)
            st.session_state.df_pets.to_csv(arq_pets, index=False)
            st.success(f"O pet {p_nome} foi salvo!")
            st.rerun()
    
    st.subheader("Lista de Animais Cadastrados")
    st.dataframe(st.session_state.df_pets, use_container_width=True)

elif menu == "💰 Financeiro":
    st.title("💰 Serviços e Recibos")
    st.info("Consulte preços ou gere um recibo rápido abaixo.")
    tab1, tab2 = st.tabs(["Tabela de Preços", "Emissão de Recibo"])
    with tab1:
        st.table({"Serviço": ["Consulta", "Vacina", "Castração"], "Valor": ["R$ 150", "R$ 130", "R$ 450"]})
    with tab2:
        r_nome = st.text_input("Nome no Recibo")
        r_serv = st.text_input("Serviço Prestado")
        r_valor = st.text_input("Valor Total")
        if st.button("GERAR"):
            st.code(f"RIBEIRA VET - RECIBO\nCliente: {r_nome}\nServiço: {r_serv}\nTotal: R$ {r_valor}\nData: {datetime.now().strftime('%d/%m/%Y')}")

elif menu == "📊 Banco de Dados":
    st.title("📊 Visão Geral do Sistema")
    c1, c2 = st.columns(2)
    c1.metric("Total de Clientes", len(st.session_state.df_tutores))
    c2.metric("Total de Pets", len(st.session_state.df_pets))
    st.divider()
    st.subheader("Download de Segurança (Backup)")
    st.download_button("Baixar Lista de Clientes", st.session_state.df_tutores.to_csv(index=False), "clientes.csv")
    st.download_button("Baixar Lista de Pets", st.session_state.df_pets.to_csv(index=False), "pets.csv")
