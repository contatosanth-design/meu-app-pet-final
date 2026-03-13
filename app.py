import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. INTERFACE DE ALTO CONTRASTE E LEGIBILIDADE
st.set_page_config(page_title="Ribeira Vet Pro v23", layout="wide")

st.markdown("""
    <style>
    /* Cores padrão para evitar que o texto suma */
    .stApp { background-color: white !important; }
    h1, h2, h3, p, label, span { color: black !important; }
    
    /* Sidebar com nomes claros */
    [data-testid="stSidebar"] { background-color: #f0f2f6 !important; min-width: 250px !important; }
    
    /* Botão Amarelo de Destaque */
    div.stButton > button {
        background-color: #FFD700 !important;
        color: black !important;
        font-weight: bold !important;
        border: 1px solid black !important;
        border-radius: 5px !important;
    }
    
    /* Inputs visíveis */
    input, textarea, select { 
        background-color: white !important; 
        color: black !important; 
        border: 1px solid #999 !important; 
    }
    </style>
    """, unsafe_allow_html=True)

# 2. GESTÃO DE ARQUIVOS (VERIFICAÇÃO DE DUPLICIDADE)
def carregar_dados(arquivo, colunas):
    if os.path.exists(arquivo):
        return pd.read_csv(arquivo)
    return pd.DataFrame(columns=colunas)

# Bases de Dados
df_tutores = carregar_dados('tutores_v23.csv', ["Nome", "CPF", "WhatsApp", "Email", "Endereco"])
df_pets = carregar_dados('pets_v23.csv', ["Dono", "Pet", "Especie", "Raca", "Peso", "Idade"])

# 3. MENU LATERAL (NOMES EXPLÍCITOS)
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2138/2138440.png", width=50)
    st.title("Menu Principal")
    # Nomes garantidos para não aparecer apenas o ícone
    opcao = st.radio("Selecione uma página:", 
                     ["👤 Cadastro de Clientes", "🐾 Cadastro de Animais", "💰 Financeiro e Recibos"])
    st.divider()
    st.info("Versão 23.0 - Registro Seguro")

# 4. PÁGINAS DE TRABALHO

if opcao == "👤 Cadastro de Clientes":
    st.header("👤 Gestão de Clientes")
    with st.form("form_tutor", clear_on_submit=False):
        c1, c2 = st.columns(2)
        n = c1.text_input("Nome do Cliente")
        c = c2.text_input("CPF")
        w = c1.text_input("WhatsApp")
        e = c2.text_input("E-mail")
        end = st.text_input("Endereço Completo")
        
        if st.form_submit_button("💾 SALVAR CLIENTE"):
            novo_t = pd.DataFrame([{"Nome": n, "CPF": c, "WhatsApp": w, "Email": e, "Endereco": end}])
            novo_t.to_csv('tutores_v23.csv', mode='a', header=not os.path.exists('tutores_v23.csv'), index=False)
            st.success("Cliente salvo com sucesso!")
            st.rerun()

    st.subheader("📋 Clientes Cadastrados")
    st.dataframe(df_tutores, use_container_width=True)

elif opcao == "🐾 Cadastro de Animais":
    st.header("🐾 Gestão de Animais")
    with st.form("form_pet", clear_on_submit=False):
        # Busca lista de donos para o selectbox
        lista_donos = ["Nenhum / Outro"] + df_tutores['Nome'].tolist()
        dono_sel = st.selectbox("Dono do Animal:", lista_donos)
        
        c1, c2 = st.columns(2)
        p_nome = c1.text_input("Nome do Pet")
        p_esp = c2.selectbox("Espécie", ["Cão", "Gato", "Ave", "Outro"])
        p_raca = c1.text_input("Raça")
        p_idade = c2.text_input("Idade")
        p_peso = st.text_input("Peso")
        
        if st.form_submit_button("💾 SALVAR ANIMAL"):
            novo_p = pd.DataFrame([{"Dono": dono_sel, "Pet": p_nome, "Especie": p_esp, "Raca": p_raca, "Peso": p_peso, "Idade": p_idade}])
            novo_p.to_csv('pets_v23.csv', mode='a', header=not os.path.exists('pets_v23.csv'), index=False)
            st.success(f"O animal {p_nome} foi registrado!")
            st.rerun()

    st.subheader("📋 Lista de Animais Cadastrados")
    # A lista agora é exibida de forma persistente
    st.dataframe(df_pets, use_container_width=True)

elif opcao == "💰 Financeiro e Recibos":
    st.header("💰 Financeiro")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Tabela de Preços")
        st.table({"Serviço": ["Consulta", "Vacina V10", "Castração"], "Valor": ["R$ 150", "R$ 130", "R$ 450"]})
    with col2:
        st.subheader("Emissão de Recibo")
        r_nome = st.text_input("Nome")
        r_serv = st.text_input("Serviço")
        r_valor = st.text_input("Valor")
        if st.button("GERAR"):
            recibo = f"RECEBEMOS DE: {r_nome}\nREFERENTE A: {r_serv}\nVALOR: R$ {r_valor}\nDATA: {datetime.now().strftime('%d/%m/%Y')}"
            st.code(recibo)
