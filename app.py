import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. TRAVA DE TEMA (FORÇA O MODO CLARO)
st.set_page_config(page_title="Ribeira Vet Pro", layout="wide", page_icon="🏥")

st.markdown("""
    <style>
    /* Forçar fundo branco e texto preto em tudo para ignorar modo escuro do PC */
    .stApp { background-color: white !important; color: #1E293B !important; }
    h1, h2, h3, h4, p, span, label { color: #1E293B !important; }
    
    /* Estilizar campos de texto para serem sempre brancos com borda cinza */
    input, textarea, select { 
        background-color: #FFFFFF !important; 
        color: #000000 !important; 
        border: 1px solid #D1D5DB !important; 
    }

    /* Cartões Coloridos (Igual ao seu exemplo de referência) */
    .card-container { display: flex; gap: 10px; margin-bottom: 20px; }
    .card {
        flex: 1; padding: 20px; border-radius: 12px; color: white !important;
        text-align: center; box-shadow: 2px 4px 8px rgba(0,0,0,0.1);
    }
    .card h2 { color: white !important; margin: 0; }
    .vencido { background-color: #EF4444; } /* Vermelho */
    .pendente { background-color: #F59E0B; } /* Laranja */
    .hoje { background-color: #3B82F6; } /* Azul */
    .total { background-color: #10B981; } /* Verde */

    /* Barra Lateral */
    [data-testid="stSidebar"] { background-color: #F3F4F6 !important; border-right: 1px solid #E5E7EB; }
    </style>
    """, unsafe_allow_html=True)

# 2. BANCO DE DADOS
def carregar_dados():
    arquivo = 'banco_vet_v8.csv'
    if os.path.exists(arquivo):
        return pd.read_csv(arquivo)
    return pd.DataFrame(columns=["ID", "Responsável", "CPF", "Animais", "Prontuário"])

if 'dados' not in st.session_state:
    st.session_state.dados = carregar_dados()

# 3. MENU LATERAL COM ÍCONES
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2138/2138440.png", width=80)
    st.markdown("## 🏥 Ribeira Vet Pro")
    menu = st.radio("Selecione a área:", ["📊 Painel Geral", "📝 Novo Cadastro", "⚕️ Prontuário & IA", "💊 Consultar Bulas"])
    st.divider()
    csv = st.session_state.dados.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Exportar Backup (Excel)", data=csv, file_name="backup_vet.csv")

# 4. PÁGINAS

if menu == "📊 Painel Geral":
    st.markdown("### 📊 Indicadores do Consultório")
    
    # Criando os cards coloridos fixos
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown('<div class="card vencido">Vencidos<h2>15</h2></div>', unsafe_allow_html=True)
    with c2: st.markdown('<div class="card pendente">Pendentes<h2>08</h2></div>', unsafe_allow_html=True)
    with c3: st.markdown('<div class="card hoje">Consultas Hoje<h2>12</h2></div>', unsafe_allow_html=True)
    with c4: st.markdown('<div class="card total">Total Clientes<h2>'+str(len(st.session_state.dados))+'</h2></div>', unsafe_allow_html=True)

    st.divider()
    st.markdown("#### 🔍 Lista Geral de Clientes")
    # Tabela editável
    df_editado = st.data_editor(st.session_state.dados, use_container_width=True, hide_index=True)
    if st.button("💾 Salvar Alterações"):
        st.session_state.dados = df_editado
        df_editado.to_csv('banco_vet_v8.csv', index=False)
        st.success("Dados salvos com sucesso!")

elif menu == "📝 Novo Cadastro":
    st.subheader("📝 Ficha de Cadastro Profissional")
    with st.form("cad_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        nome = col1.text_input("Nome do Responsável")
        cpf = col1.text_input("CPF")
        pets = col2.text_area("Animais (Nome, Espécie, Raça)")
        
        if st.form_submit_button("Finalizar Registro"):
            nova_linha = pd.DataFrame([{"ID": datetime.now().strftime("%Y%m%d%H%M"), "Responsável": nome, "CPF": cpf, "Animais": pets, "Prontuário": "Sem histórico"}])
            st.session_state.dados = pd.concat([st.session_state.dados, nova_linha], ignore_index=True)
            st.session_state.dados.to_csv('banco_vet_v8.csv', index=False)
            st.balloons()
            st.success("Cadastrado!")

elif menu == "⚕️ Prontuário & IA":
    st.subheader("⚕️ Prontuário Digital")
    if not st.session_state.dados.empty:
        cliente = st.selectbox("Selecione o Cliente:", st.session_state.dados["Responsável"].unique())
        idx = st.session_state.dados[st.session_state.dados["Responsável"] == cliente].index[0]
        
        # IA de assistência técnica
        with st.expander("🤖 Assistente de IA - Sugestão de Protocolo", expanded=True):
            st.write("💡 **Dica Clínica:** Baseado na espécie relatada, verifique o protocolo vacinal anual e controle de ectoparasitas.")
        
        evolucao = st.text_area("Evolução Clínica / Anamnese", value=st.session_state.dados.at[idx, "Prontuário"], height=300)
        if st.button("Gravar no Prontuário"):
            st.session_state.dados.at[idx, "Prontuário"] = evolucao
            st.session_state.dados.to_csv('banco_vet_v8.csv', index=False)
            st.success("Prontuário atualizado!")
    else:
        st.warning("Nenhum cliente cadastrado.")

elif menu == "💊 Consultar Bulas":
    st.subheader("💊 Bulário e Assistência")
    st.info("Digite o nome do fármaco para ver as indicações básicas.")
    st.text_input("Buscar medicamento:")
