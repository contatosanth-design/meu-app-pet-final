
import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, date

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Ribeira Vet Pro AI", layout="wide", page_icon="🐾")

# --- DESIGN MODERNO (CSS INJECTION) ---
st.markdown("""
    <style>
    /* Fundo e Fontes */
    .main { background-color: #f8fafc; font-family: 'Inter', sans-serif; }
    
    /* Cards de Métricas */
    .stMetric {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        border-bottom: 4px solid #3b82f6;
    }
    
    /* Botões Profissionais */
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        background-color: #3b82f6;
        color: white;
        font-weight: bold;
        border: none;
        transition: 0.3s;
    }
    .stButton>button:hover { background-color: #2563eb; box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4); }
    
    /* Tabelas e Inputs */
    .stTextInput>div>div>input { border-radius: 10px; }
    .stTextArea>div>div>textarea { border-radius: 10px; }
    
    /* Sidebar Custom */
    [data-testid="stSidebar"] { background-color: #1e293b; }
    [data-testid="stSidebar"] .stMarkdown { color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- BANCO DE DADOS (SQLite) ---
conn = sqlite3.connect("ribeira_pro_v7.db", check_same_thread=False)
c = conn.cursor()

def init_db():
    c.execute("CREATE TABLE IF NOT EXISTS tutores (id INTEGER PRIMARY KEY, nome TEXT, zap TEXT, endereco TEXT, cpf TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS pets (id INTEGER PRIMARY KEY, nome TEXT, raca TEXT, nasc TEXT, tutor_id INTEGER)")
    c.execute("CREATE TABLE IF NOT EXISTS prontuario (id INTEGER PRIMARY KEY, pet_id INTEGER, data TEXT, anamnese TEXT, conduta TEXT, valor REAL)")
    c.execute("CREATE TABLE IF NOT EXISTS financeiro (id INTEGER PRIMARY KEY, data TEXT, desc TEXT, valor REAL)")
    conn.commit()

init_db()

# --- NAVEGAÇÃO LATERAL ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/194/194279.png", width=80)
    st.title("Ribeira Vet Pro")
    menu = st.radio("MENU PRINCIPAL", ["🏠 Dashboard", "👥 Tutores", "🐾 Pacientes", "🩺 Atendimento", "💰 Financeiro", "⚙️ Dados"])
    st.divider()
    st.caption("Versão 7.0 - Estabilidade Total")

# --- 1. DASHBOARD (VISUAL MODERNO) ---
if menu == "🏠 Dashboard":
    st.title("Resumo da Clínica")
    c1, c2, c3, c4 = st.columns(4)
    
    total_tutores = c.execute("SELECT COUNT(*) FROM tutores").fetchone()[0]
    total_pets = c.execute("SELECT COUNT(*) FROM pets").fetchone()[0]
    faturamento = c.execute("SELECT SUM(valor) FROM financeiro").fetchone()[0] or 0
    
    c1.metric("Clientes", total_tutores)
    c2.metric("Pacientes", total_pets)
    c3.metric("Faturamento", f"R$ {faturamento:.2f}")
    c4.metric("Atendimentos", c.execute("SELECT COUNT(*) FROM prontuario").fetchone()[0])
    
    st.divider()
    st.subheader("Atividades Recentes")
    recentes = c.execute("SELECT data, desc, valor FROM financeiro ORDER BY id DESC LIMIT 5").fetchall()
    if recentes:
        st.table(pd.DataFrame(recentes, columns=["Data", "Descrição", "Valor (R$)"]))

# --- 2. TUTORES ---
elif menu == "👥 Tutores":
    st.header("Gestão de Clientes")
    with st.expander("➕ Cadastrar Novo Tutor", expanded=True):
        with st.form("tutor_form"):
            col1, col2 = st.columns(2)
            nome = col1.text_input("Nome Completo").upper()
            cpf = col2.text_input("CPF")
            zap = col1.text_input("WhatsApp")
            end = col2.text_input("Endereço Completo")
            if st.form_submit_button("SALVAR CLIENTE"):
                if nome and zap:
                    c.execute("INSERT INTO tutores (nome, zap, endereco, cpf) VALUES (?,?,?,?)", (nome, zap, end, cpf))
                    conn.commit()
                    st.success("Tutor cadastrado com sucesso!")
                    st.rerun()

    st.subheader("Lista de Tutores")
    busca = st.text_input("🔍 Pesquisar Tutor")
    lista = c.execute("SELECT nome, zap, endereco FROM tutores WHERE nome LIKE ?", (f"%{busca}%",)).fetchall()
    st.dataframe(pd.DataFrame(lista, columns=["Nome", "WhatsApp", "Endereço"]), use_container_width=True)

# --- 3. PACIENTES ---
elif menu == "🐾 Pacientes":
    st.header("Prontuário de Pacientes")
    tutores = c.execute("SELECT id, nome FROM tutores").fetchall()
    if not tutores:
        st.warning("Cadastre um tutor primeiro.")
    else:
        with st.form("pet_form"):
            tutor_id = st.selectbox("Responsável", tutores, format_func=lambda x: x[1])
            col1, col2 = st.columns(2)
            nome_p = col1.text_input("Nome do Pet").upper()
            raca = col2.selectbox("Raça", ["SRD", "Shih Tzu", "Poodle", "Pinscher", "Golden Retriever", "Bulldog", "Persa", "Siamês", "Outra"])
            nasc = st.date_input("Data de Nascimento", format="DD/MM/YYYY")
            if st.form_submit_button("CADASTRAR PET"):
                c.execute("INSERT INTO pets (nome, raca, nasc, tutor_id) VALUES (?,?,?,?)", (nome_p, raca, str(nasc), tutor_id[0]))
                conn.commit()
                st.success(f"{nome_p} cadastrado!")

# --- 4. ATENDIMENTO (O CORAÇÃO DO SISTEMA) ---
elif menu == "🩺 Atendimento":
    st.header("Consulta Médica")
    pets = c.execute("""SELECT pets.id, pets.nome, pets.raca, tutores.nome 
                        FROM pets JOIN tutores ON pets.tutor_id = tutores.id""").fetchall()
    
    if not pets:
        st.info("Nenhum paciente cadastrado.")
    else:
        pet_sel = st.selectbox("Selecionar Paciente", pets, format_func=lambda x: f"🐾 {x[1]} ({x[2]}) - Dono: {x[3]}")
        
        # Sistema de ABAS Estilo Simples.vet
        aba1, aba2, aba3 = st.tabs(["📝 Novo Prontuário", "📜 Histórico", "🔬 Exames/Vacinas"])
        
        with aba1:
            st.markdown("#### Registro Clínico (Dite com Win + H)")
            anamnese = st.text_area("Anamnese e Sintomas", height=150, placeholder="O que o pet apresenta?")
            conduta = st.text_area("Conduta e Receituário", height=150, placeholder="Qual o tratamento?")
            col_v, col_b = st.columns([1, 2])
            valor = col_v.number_input("Valor da Consulta", min_value=0.0, step=10.0)
            if st.button("🏁 FINALIZAR E COBRAR"):
                data_hoje = datetime.now().strftime("%d/%m/%Y")
                # Grava Prontuário
                c.execute("INSERT INTO prontuario (pet_id, data, anamnese, conduta, valor) VALUES (?,?,?,?,?)", 
                          (pet_sel[0], data_hoje, anamnese, conduta, valor))
                # Grava Financeiro
                c.execute("INSERT INTO financeiro (data, desc, valor) VALUES (?,?,?)", 
                          (data_hoje, f"Consulta: {pet_sel[1]}", valor))
                conn.commit()
                st.balloons()
                st.success("Atendimento registrado no histórico e no financeiro!")

        with aba2:
            historico = c.execute("SELECT data, anamnese, conduta FROM prontuario WHERE pet_id = ? ORDER BY id DESC", (pet_sel[0],)).fetchall()
            for h in historico:
                with st.expander(f"Consulta em {h[0]}"):
                    st.write(f"**Sintomas:** {h[1]}")
                    st.write(f"**Conduta:** {h[2]}")

# --- 5. FINANCEIRO ---
elif menu == "💰 Financeiro":
    st.header("Fluxo de Caixa")
    dados_fin = c.execute("SELECT data, desc, valor FROM financeiro ORDER BY id DESC").fetchall()
    if dados_fin:
        df_fin = pd.DataFrame(dados_fin, columns=["Data", "Descrição", "Valor (R$)"])
        st.dataframe(df_fin, use_container_width=True)
        st.download_button("📥 Exportar para Excel", df_fin.to_csv(), "financeiro.csv")
    else:
        st.info("Nenhuma movimentação financeira.")

# --- 6. DADOS (BACKUP) ---
elif menu == "⚙️ Dados":
    st.header("Configurações de Dados")
    st.warning("Cuidado: A limpeza de dados é irreversível.")
    if st.button("🚨 LIMPAR TODO O SISTEMA"):
        c.execute("DROP TABLE IF EXISTS tutores")
        c.execute("DROP TABLE IF EXISTS pets")
        c.execute("DROP TABLE IF EXISTS prontuario")
        c.execute("DROP TABLE IF EXISTS financeiro")
        conn.commit()
        st.rerun()
