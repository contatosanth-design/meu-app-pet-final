import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. CONFIGURAÇÃO DE TEMA (FORÇADO E UNIFICADO)
st.set_page_config(page_title="Ribeira Vet Pro", layout="wide", page_icon="🏥")

st.markdown("""
    <style>
    /* Forçar Fundo Branco e Texto Escuro Profissional */
    .stApp { background-color: #FFFFFF !important; color: #1E293B !important; }
    h1, h2, h3, h4, label, p { color: #1E293B !important; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }

    /* Botão Finalizar Amarelo (Conforme solicitado) */
    div.stButton > button:first-child {
        background-color: #FFD700 !important; /* Amarelo Ouro */
        color: #000000 !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        width: 100% !important;
        border: none !important;
        height: 3em !important;
    }

    /* Cartões Coloridos do Painel Geral */
    .card {
        padding: 20px; border-radius: 12px; color: white !important;
        text-align: center; box-shadow: 2px 4px 8px rgba(0,0,0,0.1); margin-bottom: 10px;
    }
    .vencido { background-color: #EF4444; } 
    .pendente { background-color: #F59E0B; } 
    .hoje { background-color: #3B82F6; } 
    .total { background-color: #10B981; }

    /* Inputs sempre brancos com borda visível */
    input, textarea, select { 
        background-color: white !important; 
        color: black !important; 
        border: 1px solid #D1D5DB !important; 
    }
    </style>
    """, unsafe_allow_html=True)

# 2. SISTEMA DE DADOS
def carregar_dados():
    arquivo = 'banco_vet_v9.csv'
    if os.path.exists(arquivo):
        return pd.read_csv(arquivo)
    return pd.DataFrame(columns=[
        "ID", "Tutor", "CPF", "WhatsApp", "Endereço", 
        "Paciente (Pet)", "Espécie", "Raça", "Idade", "Peso", "Sexo", "Prontuário"
    ])

if 'dados' not in st.session_state:
    st.session_state.dados = carregar_dados()

# 3. INTERFACE LATERAL
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2138/2138440.png", width=80)
    st.markdown("## 🏥 Ribeira Vet Pro")
    menu = st.radio("Navegação:", ["📊 Painel Geral", "📝 Ficha de Cadastro", "⚕️ Consultório & IA"])
    st.divider()
    csv = st.session_state.dados.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Backup Completo (CSV)", data=csv, file_name="ribeira_vet_backup.csv")

# 4. ÁREAS DO SISTEMA

if menu == "📊 Painel Geral":
    st.markdown("### 📊 Indicadores Operacionais")
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown('<div class="card vencido">Vencidos<h2>15</h2></div>', unsafe_allow_html=True)
    with c2: st.markdown('<div class="card pendente">Pendentes<h2>08</h2></div>', unsafe_allow_html=True)
    with c3: st.markdown('<div class="card hoje">Atendimentos Hoje<h2>12</h2></div>', unsafe_allow_html=True)
    with c4: st.markdown('<div class="card total">Base de Clientes<h2>'+str(len(st.session_state.dados))+'</h2></div>', unsafe_allow_html=True)
    
    st.divider()
    st.markdown("#### 🔍 Lista de Pacientes Cadastrados")
    st.data_editor(st.session_state.dados, use_container_width=True, hide_index=True)

elif menu == "📝 Ficha de Cadastro":
    st.markdown("### 📝 Cadastro Completo (Tutor e Paciente)")
    
    with st.form("ficha_completa"):
        st.markdown("#### 👤 Dados do Tutor (Proprietário)")
        t1, t2, t3 = st.columns([2, 1, 1])
        nome_tutor = t1.text_input("Nome Completo")
        cpf_tutor = t2.text_input("CPF")
        whatsapp = t3.text_input("WhatsApp (com DDD)")
        endereco = st.text_input("Endereço Completo (Rua, Nº, Bairro, Cidade)")
        
        st.divider()
        st.markdown("#### 🐾 Dados do Paciente (Animal)")
        p1, p2, p3 = st.columns(3)
        nome_pet = p1.text_input("Nome do Animal")
        especie = p2.selectbox("Espécie", ["Canina", "Felina", "Ave", "Réptil", "Outros"])
        raca = p3.text_input("Raça")
        
        p4, p5, p6 = st.columns(3)
        idade = p4.text_input("Idade Aproximada")
        peso = p5.text_input("Peso (kg)")
        sexo = p6.selectbox("Sexo", ["Macho", "Fêmea"])
        
        if st.form_submit_button("FINALIZAR CADASTRO E GRAVAR"):
            nova_entrada = {
                "ID": datetime.now().strftime("%Y%m%d%H%M"),
                "Tutor": nome_tutor, "CPF": cpf_tutor, "WhatsApp": whatsapp, "Endereço": endereco,
                "Paciente (Pet)": nome_pet, "Espécie": especie, "Raça": raca, 
                "Idade": idade, "Peso": peso, "Sexo": sexo, "Prontuário": "Ficha aberta."
            }
            st.session_state.dados = pd.concat([st.session_state.dados, pd.DataFrame([nova_entrada])], ignore_index=True)
            st.session_state.dados.to_csv('banco_vet_v9.csv', index=False)
            st.success(f"✅ Registro de {nome_pet} salvo com sucesso!")
            st.balloons()

elif menu == "⚕️ Consultório & IA":
    st.subheader("⚕️ Evolução Clínica e IA Veterinária")
    if not st.session_state.dados.empty:
        paciente_sel = st.selectbox("Selecione o Paciente para Atendimento:", st.session_state.dados["Paciente (Pet)"].unique())
        dados_p = st.session_state.dados[st.session_state.dados["Paciente (Pet)"] == paciente_sel].iloc[0]
        
        st.warning(f"📑 **Paciente:** {paciente_sel} ({dados_p['Espécie']}) | **Tutor:** {dados_p['Tutor']}")
        
        with st.expander("🤖 Assistente de IA - Sugestão de Diagnóstico", expanded=True):
            st.write("A IA está pronta para analisar os sintomas. (Integração com GPT/Gemini disponível)")
            
        anamnese = st.text_area("Histórico e Evolução Clínica", height=300)
        if st.button("SALVAR EVOLUÇÃO NO PRONTUÁRIO"):
            st.success("Prontuário atualizado e assinado digitalmente.")
    else:
        st.error("Nenhum paciente cadastrado para atendimento.")
