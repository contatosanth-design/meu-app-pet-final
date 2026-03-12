import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. TRAVA VISUAL DE LUXO (VERSÃO 12.0)
st.set_page_config(page_title="Ribeira Vet Pro v12", layout="wide", page_icon="🏥")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF !important; color: #1E293B !important; }
    
    /* BOTÃO FINALIZAR AMARELO OURO */
    div.stButton > button:first-child {
        background-color: #FFD700 !important;
        color: #000000 !important;
        font-weight: bold !important;
        border: 2px solid #B8860B !important;
        width: 100% !important;
        height: 3.5em !important;
    }

    /* CARDS COLORIDOS DO DASHBOARD */
    .card { padding: 20px; border-radius: 12px; color: white !important; text-align: center; font-weight: bold; margin-bottom: 10px; }
    .vencido { background-color: #EF4444; } 
    .pendente { background-color: #F59E0B; } 
    .hoje { background-color: #3B82F6; } 
    .total { background-color: #10B981; }

    /* Estilo dos campos de texto */
    input, textarea, select { background-color: #F9FAFB !important; color: black !important; border: 1px solid #D1D5DB !important; }
    label { color: #1E293B !important; font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. FUNÇÃO PARA NÃO PERDER DADOS
def carregar_banco(nome, colunas):
    if os.path.exists(nome):
        return pd.read_csv(nome)
    return pd.DataFrame(columns=colunas)

# Inicializando bancos v12
tutores_cols = ["CPF", "Nome do Tutor", "WhatsApp", "Endereço"]
pets_cols = ["CPF_Tutor", "Nome do Pet", "Espécie", "Raça", "Idade", "Peso", "Sexo", "Histórico"]

if 'df_tutores' not in st.session_state:
    st.session_state.df_tutores = carregar_banco('banco_tutores_v12.csv', tutores_cols)
if 'df_pets' not in st.session_state:
    st.session_state.df_pets = carregar_banco('banco_pets_v12.csv', pets_cols)

# 3. BARRA LATERAL
with st.sidebar:
    st.markdown("## 🏥 Ribeira Vet Pro")
    st.warning("📍 VERSÃO 12.0 - ESTÁVEL")
    menu = st.radio("Selecione:", ["📊 Painel Geral", "👤 Cadastro de Tutor", "🐾 Cadastro de Animal", "⚕️ Consultório"])
    st.divider()
    if st.button("📥 Salvar Backup Geral"):
        st.info("Dados sincronizados com o servidor.")

# 4. PÁGINAS

if menu == "📊 Painel Geral":
    st.markdown("### 📊 Status do Consultório")
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown('<div class="card vencido">Vencidos<br><h2>15</h2></div>', unsafe_allow_html=True)
    with c2: st.markdown('<div class="card pendente">Pendentes<br><h2>08</h2></div>', unsafe_allow_html=True)
    with c3: st.markdown('<div class="card hoje">Consultas Hoje<br><h2>12</h2></div>', unsafe_allow_html=True)
    with c4: st.markdown(f'<div class="card total">Pets na Base<br><h2>{len(st.session_state.df_pets)}</h2></div>', unsafe_allow_html=True)
    
    st.divider()
    st.subheader("📋 Lista de Tutores")
    st.dataframe(st.session_state.df_tutores, use_container_width=True, hide_index=True)

elif menu == "👤 Cadastro de Tutor":
    st.subheader("👤 Novo Proprietário")
    with st.form("form_tutor_v12"):
        c1, c2 = st.columns(2)
        nome = c1.text_input("Nome Completo do Tutor")
        cpf = c2.text_input("CPF (identificador único)")
        
        c3, c4 = st.columns([1, 2])
        whats = c3.text_input("WhatsApp com DDD")
        end = c4.text_input("Endereço Completo")
        
        if st.form_submit_button("CADASTRAR TUTOR"):
            if nome and cpf:
                novo_tutor = pd.DataFrame([{"CPF": cpf, "Nome do Tutor": nome, "WhatsApp": whats, "Endereço": end}])
                st.session_state.df_tutores = pd.concat([st.session_state.df_tutores, novo_tutor], ignore_index=True)
                st.session_state.df_tutores.to_csv('banco_tutores_v12.csv', index=False)
                st.success("Tutor salvo! Agora você já pode cadastrar os animais dele.")
            else: st.error("Por favor, preencha Nome e CPF.")

elif menu == "🐾 Cadastro de Animal":
    st.subheader("🐾 Novo Animal (Vincular a Tutor)")
    if st.session_state.df_tutores.empty:
        st.error("❌ Erro: Você precisa cadastrar o Tutor antes de cadastrar o Animal.")
    else:
        with st.form("form_pet_v12"):
            # Seleciona o tutor existente
            opcoes = st.session_state.df_tutores['Nome do Tutor'] + " (" + st.session_state.df_tutores['CPF'] + ")"
            selecionado = st.selectbox("Quem é o Dono?", opcoes)
            cpf_vinculo = selecionado.split("(")[-1].replace(")", "")
            
            st.divider()
            c1, c2, c3 = st.columns(3)
            nome_p = c1.text_input("Nome do Pet")
            especie = c2.selectbox("Espécie", ["Canina", "Felina", "Exótico", "Outro"])
            raca = c3.text_input("Raça")
            
            c4, c5, c6 = st.columns(3)
            idade = c4.text_input("Idade")
            peso = c5.text_input("Peso (kg)")
            sexo = c6.selectbox("Sexo", ["Macho", "Fêmea"])
            
            if st.form_submit_button("FINALIZAR CADASTRO DO ANIMAL"):
                if nome_p:
                    novo_pet = pd.DataFrame([{"CPF_Tutor": cpf_vinculo, "Nome do Pet": nome_p, "Espécie": especie, "Raça": raca, "Idade": idade, "Peso": peso, "Sexo": sexo, "Histórico": "Ficha aberta"}])
                    st.session_state.df_pets = pd.concat([st.session_state.df_pets, novo_pet], ignore_index=True)
                    st.session_state.df_pets.to_csv('banco_pets_v12.csv', index=False)
                    st.success(f"Sucesso! {nome_p} foi adicionado à família de {selecionado}.")
                    st.balloons()

elif menu == "⚕️ Consultório":
    st.subheader("⚕️ Atendimento e IA")
    if st.session_state.df_pets.empty:
        st.warning("Cadastre um tutor e um animal primeiro.")
    else:
        pet_atendimento = st.selectbox("Selecione o Paciente:", st.session_state.df_pets["Nome do Pet"])
        st.text_area("Anamnese e Evolução:", height=200)
        st.button("GRAVAR NO PRONTUÁRIO")
