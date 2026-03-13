import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. CONFIGURAÇÃO E ESTILO "CLEAN PRO"
st.set_page_config(page_title="Ribeira Vet Pro v19", layout="wide", page_icon="🏥")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF !important; color: #1E293B !important; }
    [data-testid="stSidebar"] { background-color: #0F172A !important; }
    [data-testid="stSidebar"] * { color: white !important; }
    
    /* Botões Amarelo Ouro - Estilo Moderno */
    div.stButton > button {
        background-color: #FFD700 !important;
        color: #000000 !important;
        font-weight: bold !important;
        border: none !important;
        border-radius: 8px !important;
        height: 3em !important;
        width: 100% !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
    }
    div.stButton > button:hover { background-color: #E6C200 !important; }

    /* Inputs Organizados */
    input, textarea, select { border: 1px solid #CBD5E1 !important; border-radius: 5px !important; }
    
    /* Cards de Informação */
    .card { background: #F8FAFC; padding: 15px; border-radius: 10px; border-left: 4px solid #FFD700; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 2. MOTOR DE DADOS (PREVENÇÃO DE DUPLICIDADE)
def gerenciar_dados(nome_arquivo, colunas):
    if not os.path.exists(nome_arquivo):
        pd.DataFrame(columns=colunas).to_csv(nome_arquivo, index=False)
    return pd.read_csv(nome_arquivo)

# Inicialização de Bases
df_tutores = gerenciar_dados('tutores_v19.csv', ["CPF", "Nome", "Email", "WhatsApp", "Endereco", "Bairro", "Cidade", "Nascimento"])
df_pets = gerenciar_dados('pets_v19.csv', ["CPF_Tutor", "Pet", "Especie", "Raca", "Sexo", "Peso", "Microchip"])
df_servicos = gerenciar_dados('catalogo_v19.csv', ["Tipo", "Item", "Preco"])
df_vendas = gerenciar_dados('vendas_v19.csv', ["Data", "Cliente", "Item", "Valor"])
df_prontuario = gerenciar_dados('prontuario_v19.csv', ["Data", "Pet", "Sintomas", "Diagnostico", "Prescricao"])

# 3. BARRA LATERAL (LOGO 40x40 E MENU)
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2138/2138440.png", width=40)
    st.title("Ribeira Vet Pro")
    menu = st.radio("Módulos de Gestão:", 
                    ["📊 Dashboard", "👤 Clientes & Pets", "⚕️ Atendimento", "💰 Financeiro & Estoque", "🤝 Relacionamento"])
    st.divider()
    st.caption("v19.0 - Estável")

# 4. LÓGICA DAS PÁGINAS

if menu == "📊 Dashboard":
    st.header("📊 Painel de Controle")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Clientes", len(df_tutores))
    col2.metric("Pets", len(df_pets))
    col3.metric("Faturamento", f"R$ {df_vendas['Valor'].sum():.2f}")
    col4.metric("Consultas", len(df_prontuario))
    
    st.subheader("Atendimentos Recentes")
    st.table(df_prontuario.tail(3))

elif menu == "👤 Clientes & Pets":
    tab1, tab2 = st.tabs(["👤 Novo Cliente", "🐾 Novo Pet"])
    
    with tab1:
        st.subheader("Cadastro de Proprietário")
        with st.form("form_tutor", clear_on_submit=True):
            c1, c2 = st.columns(2)
            nome = c1.text_input("Nome Completo")
            cpf = c2.text_input("CPF (Apenas números)")
            email = c1.text_input("E-mail")
            whats = c2.text_input("WhatsApp")
            end = st.text_input("Endereço (Rua, Nº)")
            c3, c4 = st.columns(2)
            bairro = c3.text_input("Bairro")
            cidade = c4.text_input("Cidade")
            if st.form_submit_button("SALVAR CLIENTE"):
                if not df_tutores[df_tutores['CPF'] == cpf].empty:
                    st.error("CPF já cadastrado!")
                elif nome and cpf:
                    novo = pd.DataFrame([{"CPF": cpf, "Nome": nome, "Email": email, "WhatsApp": whats, "Endereco": end, "Bairro": bairro, "Cidade": cidade}])
                    novo.to_csv('tutores_v19.csv', mode='a', header=False, index=False)
                    st.success("Cliente cadastrado com sucesso!")
                    st.rerun()

    with tab2:
        st.subheader("Cadastro de Animal")
        if df_tutores.empty: st.warning("Cadastre um cliente primeiro.")
        else:
            with st.form("form_pet"):
                tutor = st.selectbox("Proprietário:", df_tutores['Nome'] + " (" + df_tutores['CPF'].astype(str) + ")")
                c1, c2 = st.columns(2)
                nome_p = c1.text_input("Nome do Pet")
                esp = c2.selectbox("Espécie", ["Canina", "Felina", "Ave", "Outros"])
                raca = c1.text_input("Raça")
                sexo = c2.radio("Sexo", ["Macho", "Fêmea"], horizontal=True)
                peso = c1.number_input("Peso (kg)", min_value=0.0)
                if st.form_submit_button("SALVAR PET"):
                    cpf_vinc = tutor.split("(")[-1].replace(")", "")
                    novo_p = pd.DataFrame([{"CPF_Tutor": cpf_vinc, "Pet": nome_p, "Especie": esp, "Raca": raca, "Sexo": sexo, "Peso": peso}])
                    novo_p.to_csv('pets_v19.csv', mode='a', header=False, index=False)
                    st.success(f"{nome_p} cadastrado!")

elif menu == "⚕️ Atendimento":
    st.header("⚕️ Prontuário Clínico")
    if df_pets.empty: st.info("Nenhum pet no sistema.")
    else:
        with st.form("atendimento"):
            pet_sel = st.selectbox("Selecionar Paciente:", df_pets['Pet'])
            sintomas = st.text_area("Anamnese / Sintomas")
            diag = st.text_area("Diagnóstico")
            presc = st.text_area("Prescrição / Tratamento")
            if st.form_submit_button("GRAVAR CONSULTA"):
                data_h = datetime.now().strftime("%d/%m/%Y %H:%M")
                novo_pr = pd.DataFrame([{"Data": data_h, "Pet": pet_sel, "Sintomas": sintomas, "Diagnostico": diag, "Prescricao": presc}])
                novo_pr.to_csv('prontuario_v19.csv', mode='a', header=False, index=False)
                st.success("Prontuário salvo!")

elif menu == "💰 Financeiro & Estoque":
    t1, t2, t3 = st.tabs(["🏷️ Catálogo", "🛒 Nova Venda", "🧾 Recibos"])
    
    with t1:
        st.subheader("Produtos e Serviços")
        with st.form("add_cat"):
            tipo = st.selectbox("Tipo", ["Serviço", "Produto"])
            item = st.text_input("Nome (Ex: Consulta, Vacina V10, Ração)")
            preco = st.number_input("Preço Sugerido", min_value=0.0)
            if st.form_submit_button("ADICIONAR AO CATÁLOGO"):
                pd.DataFrame([{"Tipo": tipo, "Item": item, "Preco": preco}]).to_csv('catalogo_v19.csv', mode='a', header=False, index=False)
                st.success("Item adicionado!")
        st.dataframe(df_servicos, use_container_width=True)

    with t2:
        st.subheader("Lançar Venda/Atendimento")
        with st.form("venda"):
            cli = st.selectbox("Cliente:", df_tutores['Nome'] if not df_tutores.empty else ["Nenhum"])
            it = st.selectbox("Item:", df_servicos['Item'] if not df_servicos.empty else ["Nenhum"])
            vlr = st.number_input("Valor Final (R$)", min_value=0.0)
            if st.form_submit_button("CONFIRMAR PAGAMENTO"):
                pd.DataFrame([{"Data": datetime.now().strftime("%d/%m/%Y"), "Cliente": cli, "Item": it, "Valor": vlr}]).to_csv('vendas_v19.csv', mode='a', header=False, index=False)
                st.success("Venda registrada!")

    with t3:
        st.subheader("Gerador de Recibo")
        venda_sel = st.selectbox("Selecione a Venda:", df_vendas.index)
        if not df_vendas.empty:
            v = df_vendas.iloc[venda_sel]
            recibo_txt = f"""
            ------------------------------------------
            RECIBO DE SERVIÇOS VETERINÁRIOS
            ------------------------------------------
            DATA: {v['Data']}
            CLIENTE: {v['Cliente']}
            ------------------------------------------
            DISCRIMINAÇÃO:
            {v['Item']} ................ R$ {v['Valor']:.2f}
            ------------------------------------------
            TOTAL: R$ {v['Valor']:.2f}
            
            Obrigado pela confiança!
            Ribeira Vet Pro
            """
            st.code(recibo_txt)
            st.button("Imprimir (Simulação)")

elif menu == "🤝 Relacionamento":
    st.header("🤝 Espaço do Cliente (CRM)")
    st.info("Aqui você monitora a frequência dos seus clientes.")
    if not df_vendas.empty:
        rank = df_vendas.groupby('Cliente')['Valor'].sum().sort_values(ascending=False)
        st.subheader("Top Clientes (por Investimento)")
        st.bar_chart(rank)
    else:
        st.write("Dados insuficientes para gerar análise.")
