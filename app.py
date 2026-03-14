import streamlit as st
import pandas as pd
import os
from datetime import datetime
import zipfile
import io
import base64
import json
import requests
from fpdf import FPDF
import tempfile
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go

# Configuração da página
st.set_page_config(page_title="Ribeira Vet Pro v24 - Completo", layout="wide")

# CSS personalizado
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa !important; }
    h1, h2, h3, p, label, span { color: #1e1e2f !important; }
    
    /* Sidebar */
    [data-testid="stSidebar"] { 
        background-color: #2b3e4f !important; 
        min-width: 280px !important;
    }
    [data-testid="stSidebar"] * { color: white !important; }
    
    /* Cards */
    .card {
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    
    /* Botões */
    div.stButton > button {
        background: linear-gradient(45deg, #FFD700, #FFA500) !important;
        color: black !important;
        font-weight: bold !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 10px 20px !important;
        transition: all 0.3s ease !important;
    }
    
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    
    /* Tabs personalizadas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: white;
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
        font-weight: 600;
    }
    
    /* Badges */
    .badge {
        display: inline-block;
        padding: 5px 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
        margin: 2px;
    }
    
    .badge-success { background-color: #d4edda; color: #155724; }
    .badge-warning { background-color: #fff3cd; color: #856404; }
    .badge-danger { background-color: #f8d7da; color: #721c24; }
    .badge-info { background-color: #d1ecf1; color: #0c5460; }
    
    /* Anamnese section */
    .anamnese-section {
        background-color: #f1f9ff;
        border-left: 4px solid #2196F3;
        padding: 15px;
        margin: 10px 0;
        border-radius: 0 8px 8px 0;
    }
    
    /* Receita section */
    .receita {
        background-color: white;
        border: 2px dashed #2b3e4f;
        padding: 30px;
        margin: 20px 0;
        font-family: 'Courier New', monospace;
    }
    
    /* Dashboard metrics */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# ==================== INICIALIZAÇÃO DO ESTADO DA SESSÃO ====================
if 'form_data' not in st.session_state:
    st.session_state.form_data = {}
if 'editando' not in st.session_state:
    st.session_state.editando = None
if 'confirmar_exclusao' not in st.session_state:
    st.session_state.confirmar_exclusao = False
if 'historico_consultas' not in st.session_state:
    st.session_state.historico_consultas = []
if 'agendamentos' not in st.session_state:
    st.session_state.agendamentos = []
if 'prontuarios' not in st.session_state:
    st.session_state.prontuarios = {}
if 'medicamentos_db' not in st.session_state:
    # Base de dados simulada de medicamentos veterinários
    st.session_state.medicamentos_db = {
        "Amoxicilina": {
            "apresentacao": "Suspensão 50mg/ml, Comprimidos 200mg",
            "indicacao": "Infecções bacterianas, respiratório, urinário, pele",
            "dosagem": "10-20mg/kg a cada 12-24h",
            "contraindicacoes": "Alergia a penicilinas, animais com insuficiência renal",
            "bula": "Antibiótico bactericida de amplo espectro. Inibe síntese da parede celular.",
            "via": "Oral, IM, SC"
        },
        "Carprofeno": {
            "apresentacao": "Comprimidos 25mg, 75mg, 100mg",
            "indicacao": "Anti-inflamatório, analgésico, pós-operatório, artrite",
            "dosagem": "2-4mg/kg a cada 24h",
            "contraindicacoes": "Úlceras gástricas, insuficiência hepática/renal",
            "bula": "AINE seletivo COX-2. Efeito analgésico e anti-inflamatório.",
            "via": "Oral"
        },
        "Doxiciclina": {
            "apresentacao": "Comprimidos 100mg",
            "indicacao": "Erliquiose, infecções respiratórias, clamidiose",
            "dosagem": "5-10mg/kg a cada 12-24h",
            "contraindicacoes": "Filhotes, animais com disfagia",
            "bula": "Tetraciclina bacteriostática de ação prolongada",
            "via": "Oral"
        },
        "Ivermectina": {
            "apresentacao": "Injetável 1%, Oral 0.6mg/ml",
            "indicacao": "Verminoses, sarna, pulgas, carrapatos",
            "dosagem": "0.2-0.4mg/kg SC ou oral",
            "contraindicacoes": "Collies e raças sensíveis, filhotes <6 semanas",
            "bula": "Antiparasitário de amplo espectro, age em canais de cloro",
            "via": "SC, Oral"
        },
        "Meloxicam": {
            "apresentacao": "Suspensão 0.5mg/ml, 2mg/ml; Injetável 2mg/ml",
            "indicacao": "Anti-inflamatório, analgésico, pós-operatório",
            "dosagem": "0.1-0.2mg/kg a cada 24h",
            "contraindicacoes": "Desidratação, hipovolemia, insuficiência renal",
            "bula": "AINE seletivo COX-2, ação prolongada",
            "via": "Oral, SC, IV"
        },
        "Omeprazol": {
            "apresentacao": "Comprimidos 10mg, 20mg",
            "indicacao": "Gastrite, úlceras, refluxo, prevenção de lesões gástricas",
            "dosagem": "0.5-1mg/kg a cada 24h",
            "contraindicacoes": "Hipersensibilidade",
            "bula": "Inibidor de bomba de prótons, reduz secreção ácida",
            "via": "Oral"
        }
    }
if 'sugestoes_diagnostico' not in st.session_state:
    # Base de conhecimento para sugestão de diagnósticos
    st.session_state.sugestoes_diagnostico = {
        "sinais_respiratorios": {
            "tosse": ["Traqueíte", "Bronquite", "Pneumonia", "Colapso de traqueia"],
            "espirros": ["Rinite", "Corpo estranho", "Alergia"],
            "secrecao_nasal": ["Gripe canina", "Cinomatose", "Sinusite"],
            "dificuldade_respiratoria": ["Edema pulmonar", "Pneumonia", "Asma felina"]
        },
        "sinais_digestivos": {
            "vomito": ["Gastrite", "Pancreatite", "Corpo estranho", "Intoxicação"],
            "diarreia": ["Parvovirose", "Gastroenterite", "Verminose", "Alimentar"],
            "falta_apetite": ["Doença sistêmica", "Dor", "Febre"],
            "disfagia": ["Corpo estranho", "Esofagite", "Tonsilite"]
        },
        "sinais_dermatologicos": {
            "prurido": ["Dermatite alérgica", "Sarna", "Pulgas"],
            "queda_pelo": ["Hipotireoidismo", "Dermatite", "Estresse"],
            "lesoes_pele": ["Piodermite", "Fungos", "Leishmaniose"],
            "descamacao": ["Seborreia", "Dermatite seborreica"]
        },
        "sinais_oftalmicos": {
            "secrecao_ocular": ["Conjuntivite", "Ceratoconjuntivite seca"],
            "vermelhidao": ["Uveíte", "Glaucoma", "Conjuntivite"],
            "opacidade": ["Catarata", "Edema de córnea", "Esclerose nuclear"]
        },
        "sinais_otologicos": {
            "coceira_ouvido": ["Otite parasitária", "Alergia"],
            "secrecao_ouvido": ["Otite bacteriana", "Otite fúngica"],
            "odor": ["Otite crônica", "Corpo estranho"]
        },
        "sinais_urogenitais": {
            "disuria": ["Cistite", "Urolitíase", "ITU"],
            "poliuria": ["Diabetes", "Insuficiência renal", "Piometra"],
            "hematúria": ["Cistite", "Urolitíase", "Neoplasia"]
        }
    }

# ==================== FUNÇÕES UTILITÁRIAS ====================
def carregar_dados(arquivo, colunas):
    if os.path.exists(arquivo):
        try:
            return pd.read_csv(arquivo)
        except:
            return pd.DataFrame(columns=colunas)
    return pd.DataFrame(columns=colunas)

def salvar_dados_com_seguranca(df, nome_arquivo):
    try:
        df.to_csv(nome_arquivo, index=False)
        return True
    except Exception as e:
        st.error(f"Erro ao salvar dados: {e}")
        return False

def criar_pdf_receita(dados_receita):
    """Gera PDF da receita veterinária"""
    pdf = FPDF()
    pdf.add_page()
    
    # Cabeçalho
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'CLÍNICA VETERINÁRIA RIBEIRA VET', 0, 1, 'C')
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, 'CNPJ: 12.345.678/0001-90', 0, 1, 'C')
    pdf.cell(0, 10, 'Tel: (11) 1234-5678', 0, 1, 'C')
    pdf.line(10, 45, 200, 45)
    
    # Dados do proprietário
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, f"Proprietário: {dados_receita['proprietario']}", 0, 1)
    pdf.cell(0, 10, f"Animal: {dados_receita['animal']} | Espécie: {dados_receita['especie']}", 0, 1)
    
    # Receita
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'RECEITA VETERINÁRIA', 0, 1, 'C')
    pdf.ln(10)
    
    pdf.set_font('Arial', '', 12)
    pdf.multi_cell(0, 10, f"Medicamento: {dados_receita['medicamento']}")
    pdf.multi_cell(0, 10, f"Apresentação: {dados_receita['apresentacao']}")
    pdf.multi_cell(0, 10, f"Posologia: {dados_receita['posologia']}")
    pdf.multi_cell(0, 10, f"Duração do tratamento: {dados_receita['duracao']}")
    
    if dados_receita.get('observacoes'):
        pdf.multi_cell(0, 10, f"Observações: {dados_receita['observacoes']}")
    
    # Data e assinatura
    pdf.ln(20)
    pdf.cell(0, 10, f"São Paulo, {datetime.now().strftime('%d/%m/%Y')}", 0, 1)
    pdf.ln(20)
    pdf.cell(0, 10, '____________________________________', 0, 1, 'C')
    pdf.cell(0, 10, 'Assinatura e Carimbo do Médico Veterinário', 0, 1, 'C')
    
    # Salvar em arquivo temporário
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    pdf.output(temp_file.name)
    return temp_file.name

def sugestao_diagnostico(sintomas):
    """Sistema especialista simples para sugestão de diagnósticos"""
    sugestoes = []
    
    if "febre" in sintomas.lower():
        sugestoes.append("Infecção bacteriana")
        sugestoes.append("Infecção viral")
        sugestoes.append("Processo inflamatório")
    
    if "vomito" in sintomas.lower() and "diarreia" in sintomas.lower():
        sugestoes.append("Gastroenterite")
        sugestoes.append("Parvovirose (se filhote não vacinado)")
        sugestoes.append("Intoxicação alimentar")
    
    if "tosse" in sintomas.lower() and "espirro" in sintomas.lower():
        sugestoes.append("Traqueobronquite infecciosa canina (Tosse dos canis)")
        sugestoes.append("Gripe canina")
        sugestoes.append("Complexo respiratório felino")
    
    if "prurido" in sintomas.lower() and "lesao_pele" in sintomas.lower():
        sugestoes.append("Dermatite alérgica")
        sugestoes.append("Sarna sarcóptica")
        sugestoes.append("Piodermite")
    
    if "poliuria" in sintomas.lower() and "polidipsia" in sintomas.lower():
        sugestoes.append("Diabetes mellitus")
        sugestoes.append("Insuficiência renal crônica")
        sugestoes.append("Hiperadrenocorticismo")
    
    if "disfagia" in sintomas.lower() or "regurgitacao" in sintomas.lower():
        sugestoes.append("Megaesôfago")
        sugestoes.append("Corpo estranho esofágico")
        sugestoes.append("Esofagite")
    
    if not sugestoes:
        sugestoes.append("Nenhum padrão específico identificado")
        sugestoes.append("Recomenda-se exames complementares")
    
    return list(set(sugestoes))  # Remove duplicatas

def get_base64_image(image_path):
    """Converte imagem para base64"""
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return None

def enviar_whatsapp(mensagem, telefone):
    """Gera link para WhatsApp"""
    # Remove caracteres não numéricos
    telefone = ''.join(filter(str.isdigit, str(telefone)))
    # Codifica a mensagem para URL
    mensagem_codificada = base64.b64encode(mensagem.encode()).decode()
    # Gera link do WhatsApp
    link = f"https://api.whatsapp.com/send?phone=55{telefone}&text={mensagem}"
    return link

# Carregar bases de dados
df_tutores = carregar_dados('tutores_v24.csv', ["Nome", "CPF", "WhatsApp", "Email", "Endereco", "DataCadastro"])
df_pets = carregar_dados('pets_v24.csv', ["Dono", "Pet", "Especie", "Raca", "Peso", "Idade", "Sexo", "DataNascimento", "Microchip", "Alergias"])
df_consultas = carregar_dados('consultas_v24.csv', ["Data", "Pet", "Dono", "Tipo", "Anamnese", "Diagnostico", "Prescricao", "Exames", "Retorno"])

# ==================== MENU PRINCIPAL ====================
with st.sidebar:
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.image("https://cdn-icons-png.flaticon.com/512/2138/2138440.png", width=80)
    
    st.title("🐕 RIBEIRA VET PRO")
    st.markdown("---")
    
    # Menu principal com ícones
    opcao = st.radio(
        "MÓDULOS DO SISTEMA:",
        ["🏥 DASHBOARD", 
         "👤 CLIENTES", 
         "🐾 ANIMAIS", 
         "📋 CONSULTAS", 
         "📜 PRONTUÁRIO",
         "💊 RECEITUÁRIO", 
         "📚 BULAS", 
         "💰 FINANCEIRO",
         "📅 AGENDA"]
    )
    
    st.markdown("---")
    
    # Estatísticas rápidas
    st.subheader("📊 RESUMO RÁPIDO")
    
    # Cards de estatísticas
    col_a, col_b = st.columns(2)
    with col_a:
        st.info(f"👥 Clientes: {len(df_tutores)}")
    with col_b:
        st.info(f"🐕 Pets: {len(df_pets)}")
    
    if st.session_state.historico_consultas:
        st.success(f"📋 Consultas: {len(st.session_state.historico_consultas)}")
    
    st.markdown("---")
    
    # Ações rápidas
    st.subheader("⚡ AÇÕES RÁPIDAS")
    if st.button("➕ NOVA CONSULTA", use_container_width=True):
        st.session_state['pagina'] = "CONSULTAS"
    
    if st.button("📝 NOVO CLIENTE", use_container_width=True):
        st.session_state['pagina'] = "CLIENTES"
    
    if st.button("💊 BULAS", use_container_width=True):
        st.session_state['pagina'] = "BULAS"
    
    st.markdown("---")
    
    # Versão e info
    st.caption("Versão 24.0 - Profissional")
    st.caption("© 2024 - Todos os direitos reservados")

# ==================== PÁGINAS ====================

if opcao == "🏥 DASHBOARD":
    st.title("🏥 Dashboard Clínico")
    
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>🐕 PACIENTES</h3>
            <h2>{}</h2>
        </div>
        """.format(len(df_pets)), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card" style="background: linear-gradient(135deg, #ff758c 0%, #ff7eb3 100%);">
            <h3>📋 CONSULTAS</h3>
            <h2>{}</h2>
        </div>
        """.format(len(st.session_state.historico_consultas)), unsafe_allow_html=True)
    
    with col3:
        valor_total = len(st.session_state.historico_consultas) * 150
        st.markdown("""
        <div class="metric-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
            <h3>💰 FATURAMENTO</h3>
            <h2>R$ {:,.2f}</h2>
        </div>
        """.format(valor_total), unsafe_allow_html=True)
    
    with col4:
        agendamentos_hoje = len([a for a in st.session_state.agendamentos 
                                if a.get('Data') == datetime.now().strftime('%d/%m/%Y')])
        st.markdown("""
        <div class="metric-card" style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);">
            <h3>📅 HOJE</h3>
            <h2>{}</h2>
        </div>
        """.format(agendamentos_hoje), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Gráficos e análises
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Distribuição por Espécie")
        if not df_pets.empty:
            especies = df_pets['Especie'].value_counts()
            fig = px.pie(values=especies.values, names=especies.index, 
                        title="Pacientes por Espécie",
                        color_discrete_sequence=px.colors.qualitative.Set3)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Nenhum animal cadastrado")
    
    with col2:
        st.subheader("📈 Consultas por Mês")
        if st.session_state.historico_consultas:
            df_cons = pd.DataFrame(st.session_state.historico_consultas)
            df_cons['Data'] = pd.to_datetime(df_cons['Data'], format='%d/%m/%Y')
            df_cons['Mês'] = df_cons['Data'].dt.month
            consultas_mes = df_cons['Mês'].value_counts().sort_index()
            
            fig = px.bar(x=consultas_mes.index, y=consultas_mes.values,
                        labels={'x':'Mês', 'y':'Nº Consultas'},
                        title="Consultas Realizadas",
                        color_discrete_sequence=['#4facfe'])
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Nenhuma consulta registrada")
    
    st.markdown("---")
    
    # Próximos agendamentos
    st.subheader("📅 Próximos Agendamentos")
    if st.session_state.agendamentos:
        df_agenda = pd.DataFrame(st.session_state.agendamentos)
        # Ordenar por data
        df_agenda['Data'] = pd.to_datetime(df_agenda['Data'], format='%d/%m/%Y')
        df_agenda = df_agenda.sort_values('Data').head(5)
        df_agenda['Data'] = df_agenda['Data'].dt.strftime('%d/%m/%Y')
        st.dataframe(df_agenda[['Data', 'Hora', 'Cliente', 'Animal', 'Tipo']], use_container_width=True)
    else:
        st.info("Nenhum agendamento futuro")

elif opcao == "👤 CLIENTES":
    st.title("👤 Gestão de Clientes")
    
    # Tabs para diferentes funcionalidades
    tab1, tab2, tab3 = st.tabs(["📝 Cadastro", "📋 Lista", "🔍 Busca"])
    
    with tab1:
        with st.form("form_cliente"):
            st.subheader("Novo Cliente")
            
            col1, col2 = st.columns(2)
            with col1:
                nome = st.text_input("Nome Completo *")
                cpf = st.text_input("CPF *", help="Apenas números")
                whatsapp = st.text_input("WhatsApp *", help="Com DDD, apenas números")
            
            with col2:
                email = st.text_input("E-mail")
                endereco = st.text_input("Endereço Completo")
                data_cadastro = datetime.now().strftime('%d/%m/%Y')
            
            observacoes = st.text_area("Observações")
            
            col1, col2, col3 = st.columns(3)
            with col2:
                submitted = st.form_submit_button("💾 SALVAR CLIENTE", use_container_width=True)
            
            if submitted:
                if not nome or not cpf or not whatsapp:
                    st.error("Preencha os campos obrigatórios!")
                else:
                    novo_cliente = pd.DataFrame([{
                        "Nome": nome,
                        "CPF": cpf,
                        "WhatsApp": whatsapp,
                        "Email": email,
                        "Endereco": endereco,
                        "DataCadastro": data_cadastro,
                        "Observacoes": observacoes
                    }])
                    
                    novo_cliente.to_csv('tutores_v24.csv', 
                                      mode='a', 
                                      header=not os.path.exists('tutores_v24.csv'), 
                                      index=False)
                    st.success("✅ Cliente cadastrado com sucesso!")
                    st.balloons()
    
    with tab2:
        st.subheader("Clientes Cadastrados")
        if not df_tutores.empty:
            # Opção de exportar
            if st.button("📥 Exportar para Excel"):
                df_tutores.to_excel("clientes_export.xlsx", index=False)
                st.success("Arquivo exportado!")
            
            st.dataframe(df_tutores, use_container_width=True)
            
            # Visualizar detalhes de um cliente
            st.subheader("Detalhes do Cliente")
            cliente_sel = st.selectbox("Selecione um cliente", df_tutores['Nome'].tolist())
            
            if cliente_sel:
                dados_cliente = df_tutores[df_tutores['Nome'] == cliente_sel].iloc[0]
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"""
                    **Nome:** {dados_cliente['Nome']}  
                    **CPF:** {dados_cliente['CPF']}  
                    **WhatsApp:** {dados_cliente['WhatsApp']}  
                    **E-mail:** {dados_cliente.get('Email', 'N/I')}
                    """)
                
                with col2:
                    st.markdown(f"""
                    **Endereço:** {dados_cliente.get('Endereco', 'N/I')}  
                    **Data Cadastro:** {dados_cliente.get('DataCadastro', 'N/I')}  
                    **Total de Animais:** {len(df_pets[df_pets['Dono'] == cliente_sel])}
                    """)
                
                # Botão WhatsApp
                if st.button(f"📱 Enviar WhatsApp para {cliente_sel}"):
                    telefone = dados_cliente['WhatsApp']
                    mensagem = f"Olá {cliente_sel}! Tudo bem? Passando para lembrar da consulta do seu pet."
                    link = enviar_whatsapp(mensagem, telefone)
                    st.markdown(f"[Clique aqui para abrir WhatsApp]({link})")
        else:
            st.info("Nenhum cliente cadastrado")
    
    with tab3:
        st.subheader("🔍 Busca Avançada")
        termo = st.text_input("Digite nome ou CPF")
        if termo:
            resultados = df_tutores[
                df_tutores['Nome'].str.contains(termo, case=False, na=False) |
                df_tutores['CPF'].str.contains(termo, na=False)
            ]
            st.write(f"Encontrados: {len(resultados)}")
            st.dataframe(resultados)

elif opcao == "🐾 ANIMAIS":
    st.title("🐾 Gestão de Animais")
    
    tab1, tab2, tab3 = st.tabs(["📝 Cadastro", "📋 Lista", "📊 Estatísticas"])
    
    with tab1:
        with st.form("form_animal"):
            st.subheader("Novo Animal")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Selecionar dono
                if not df_tutores.empty:
                    dono = st.selectbox("Proprietário *", df_tutores['Nome'].tolist())
                else:
                    st.error("Cadastre um cliente primeiro!")
                    dono = None
                
                nome_pet = st.text_input("Nome do Animal *")
                especie = st.selectbox("Espécie *", ["Cão", "Gato", "Ave", "Roedor", "Réptil", "Outro"])
                raca = st.text_input("Raça")
                sexo = st.radio("Sexo", ["Macho", "Fêmea"], horizontal=True)
            
            with col2:
                data_nasc = st.date_input("Data de Nascimento", 
                                         min_value=datetime(1990,1,1),
                                         max_value=datetime.now())
                peso = st.number_input("Peso (kg)", min_value=0.0, max_value=100.0, step=0.1)
                microchip = st.text_input("Nº Microchip")
                cor = st.text_input("Cor/Pelagem")
            
            alergias = st.text_area("Alergias conhecidas")
            observacoes = st.text_area("Observações importantes")
            
            col1, col2, col3 = st.columns(3)
            with col2:
                submitted = st.form_submit_button("💾 SALVAR ANIMAL", use_container_width=True)
            
            if submitted and dono and nome_pet:
                # Calcular idade
                idade_dias = (datetime.now() - data_nasc).days
                idade_anos = idade_dias // 365
                idade_meses = (idade_dias % 365) // 30
                idade_str = f"{idade_anos} anos e {idade_meses} meses" if idade_anos > 0 else f"{idade_meses} meses"
                
                novo_pet = pd.DataFrame([{
                    "Dono": dono,
                    "Pet": nome_pet,
                    "Especie": especie,
                    "Raca": raca,
                    "Sexo": sexo,
                    "DataNascimento": data_nasc.strftime('%d/%m/%Y'),
                    "Idade": idade_str,
                    "Peso": peso,
                    "Microchip": microchip,
                    "Cor": cor,
                    "Alergias": alergias,
                    "Observacoes": observacoes,
                    "DataCadastro": datetime.now().strftime('%d/%m/%Y')
                }])
                
                novo_pet.to_csv('pets_v24.csv', 
                              mode='a', 
                              header=not os.path.exists('pets_v24.csv'), 
                              index=False)
                st.success(f"✅ {nome_pet} cadastrado com sucesso!")
                st.balloons()
    
    with tab2:
        st.subheader("Animais Cadastrados")
        if not df_pets.empty:
            # Filtros
            col1, col2, col3 = st.columns(3)
            with col1:
                filtro_especie = st.selectbox("Filtrar por espécie", ["Todos"] + df_pets['Especie'].unique().tolist())
            with col2:
                filtro_dono = st.selectbox("Filtrar por dono", ["Todos"] + df_pets['Dono'].unique().tolist())
            with col3:
                filtro_sexo = st.selectbox("Filtrar por sexo", ["Todos", "Macho", "Fêmea"])
            
            df_filtrado = df_pets.copy()
            if filtro_especie != "Todos":
                df_filtrado = df_filtrado[df_filtrado['Especie'] == filtro_especie]
            if filtro_dono != "Todos":
                df_filtrado = df_filtrado[df_filtrado['Dono'] == filtro_dono]
            if filtro_sexo != "Todos":
                df_filtrado = df_filtrado[df_filtrado['Sexo'] == filtro_sexo]
            
            st.dataframe(df_filtrado, use_container_width=True)
            
            # Ver detalhes do animal
            st.subheader("Detalhes do Animal")
            animal_sel = st.selectbox("Selecione um animal", df_filtrado['Pet'].tolist())
            
            if animal_sel:
                dados_animal = df_filtrado[df_filtrado['Pet'] == animal_sel].iloc[0]
                
                # Card de informações
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"""
                    **Animal:** {dados_animal['Pet']}  
                    **Espécie:** {dados_animal['Especie']}  
                    **Raça:** {dados_animal.get('Raca', 'N/I')}  
                    **Sexo:** {dados_animal.get('Sexo', 'N/I')}  
                    **Idade:** {dados_animal.get('Idade', 'N/I')}  
                    **Peso:** {dados_animal.get('Peso', 'N/I')} kg
                    """)
                
                with col2:
                    st.markdown(f"""
                    **Proprietário:** {dados_animal['Dono']}  
                    **Microchip:** {dados_animal.get('Microchip', 'N/I')}  
                    **Cor:** {dados_animal.get('Cor', 'N/I')}  
                    **Alergias:** {dados_animal.get('Alergias', 'N/I')}
                    """)
                
                # Botão para iniciar consulta
                if st.button("🩺 INICIAR CONSULTA", use_container_width=True):
                    st.session_state['animal_consulta'] = animal_sel
                    st.session_state['pagina'] = "CONSULTAS"
                    st.rerun()
        else:
            st.info("Nenhum animal cadastrado")
    
    with tab3:
        st.subheader("Estatísticas dos Animais")
        if not df_pets.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                # Gráfico de espécies
                especies = df_pets['Especie'].value_counts()
                fig = px.pie(values=especies.values, names=especies.index, title="Distribuição por Espécie")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Gráfico de sexo
                sexo = df_pets['Sexo'].value_counts()
                fig = px.bar(x=sexo.index, y=sexo.values, title="Distribuição por Sexo")
                st.plotly_chart(fig, use_container_width=True)
            
            # Top 5 raças
            st.subheader("Top 5 Raças")
            racas = df_pets['Raca'].value_counts().head()
            st.dataframe(racas)

elif opcao == "📋 CONSULTAS":
    st.title("🩺 Consultas Clínicas")
    
    tab1, tab2, tab3 = st.tabs(["📝 Nova Consulta", "📋 Histórico", "🔍 Anamnese Rápida"])
    
    with tab1:
        st.markdown("""
        <div class="anamnese-section">
            <h3>📋 REGISTRO DE CONSULTA - SOAP</h3>
            <p>Preencha os dados abaixo para registrar a consulta</p>
        </div>
        """, unsafe_allow_html=True)
        
        if not df_pets.empty:
            with st.form("form_consulta"):
                col1, col2 = st.columns(2)
                
                with col1:
                    # Selecionar animal
                    animal = st.selectbox("Animal *", df_pets['Pet'].tolist())
                    
                    # Buscar dono automaticamente
                    dono = df_pets[df_pets['Pet'] == animal]['Dono'].iloc[0]
                    st.info(f"🐕 Proprietário: {dono}")
                    
                    data_consulta = st.date_input("Data da Consulta", datetime.now())
                    tipo_consulta = st.selectbox("Tipo de Consulta", 
                                                ["Primeira Consulta", "Retorno", "Emergência", "Vacinação", "Check-up"])
                
                with col2:
                    temperatura = st.number_input("Temperatura (°C)", min_value=35.0, max_value=42.0, step=0.1)
                    fc = st.number_input("Frequência Cardíaca (bpm)", min_value=0, max_value=300)
                    fr = st.number_input("Frequência Respiratória (mpm)", min_value=0, max_value=200)
                    tpc = st.number_input("TPC (segundos)", min_value=0, max_value=5)
                    peso = st.number_input("Peso atual (kg)", min_value=0.0, step=0.1)
                
                st.markdown("---")
                
                # SOAP - Subjetivo
                st.subheader("S - Subjetivo (História e Queixa)")
                queixa = st.text_area("Queixa Principal", placeholder="O que o tutor relata?")
                historico = st.text_area("Histórico da Doença Atual", placeholder="Quando começou? Evolução?")
                
                # SOAP - Objetivo
                st.subheader("O - Objetivo (Achados do Exame Físico)")
                col1, col2 = st.columns(2)
                with col1:
                    mucosa = st.selectbox("Mucosas", ["Normocoradas", "Hipocoradas", "Hiperêmicas", "Ictéricas", "Cianóticas"])
                    hidratacao = st.selectbox("Hidratação", ["Normal", "Leve desidratação", "Moderada", "Grave"])
                    linfonodos = st.selectbox("Linfonodos", ["Normais", "Reativos", "Aumentados"])
                
                with col2:
                    auscultacao = st.text_area("Ausculta Cardiopulmonar")
                    palpacao = st.text_area("Palpação Abdominal")
                    outros = st.text_area("Outros achados")
                
                # SOAP - Avaliação
                st.subheader("A - Avaliação (Diagnóstico Presuntivo)")
                
                # Campo para sintomas (para sugestão automática)
                sintomas_text = st.text_area("Descreva os sintomas observados", 
                                           placeholder="Ex: febre, vômito, diarreia, tosse...")
                
                # Botão para sugestão de diagnóstico
                if st.form_submit_button("🔍 SUGERIR DIAGNÓSTICOS"):
                    if sintomas_text:
                        sugestoes = sugestao_diagnostico(sintomas_text)
                        st.session_state['sugestoes_temp'] = sugestoes
                
                # Mostrar sugestões se existirem
                if 'sugestoes_temp' in st.session_state:
                    st.success("Diagnósticos sugeridos:")
                    for i, sug in enumerate(st.session_state['sugestoes_temp'], 1):
                        st.write(f"{i}. {sug}")
                
                diagnostico = st.text_area("Diagnóstico (definitivo ou presuntivo)", 
                                          value=", ".join(st.session_state.get('sugestoes_temp', [])) if 'sugestoes_temp' in st.session_state else "")
                
                # SOAP - Plano
                st.subheader("P - Plano (Tratamento e Conduta)")
                exames = st.text_area("Exames solicitados")
                tratamento = st.text_area("Tratamento prescrito")
                orientacoes = st.text_area("Orientações ao tutor")
                retorno = st.number_input("Retorno em (dias)", min_value=0, max_value=90, value=0)
                
                col1, col2, col3 = st.columns(3)
                with col2:
                    submitted = st.form_submit_button("💾 FINALIZAR CONSULTA", use_container_width=True)
                
                if submitted:
                    if not queixa or not diagnostico:
                        st.error("Preencha pelo menos a queixa principal e o diagnóstico!")
                    else:
                        # Salvar consulta
                        consulta = {
                            "Data": data_consulta.strftime('%d/%m/%Y'),
                            "Animal": animal,
                            "Dono": dono,
                            "Tipo": tipo_consulta,
                            "S_Queixa": queixa,
                            "S_Historico": historico,
                            "O_Temperatura": temperatura,
                            "O_FC": fc,
                            "O_FR": fr,
                            "O_Mucosa": mucosa,
                            "O_Hidratacao": hidratacao,
                            "A_Diagnostico": diagnostico,
                            "P_Exames": exames,
                            "P_Tratamento": tratamento,
                            "P_Orientacoes": orientacoes,
                            "P_Retorno": retorno
                        }
                        
                        st.session_state.historico_consultas.append(consulta)
                        
                        # Atualizar prontuário do animal
                        if animal not in st.session_state.prontuarios:
                            st.session_state.prontuarios[animal] = []
                        st.session_state.prontuarios[animal].append(consulta)
                        
                        # Salvar em CSV
                        df_cons = pd.DataFrame([consulta])
                        df_cons.to_csv('consultas_v24.csv', 
                                      mode='a', 
                                      header=not os.path.exists('consultas_v24.csv'), 
                                      index=False)
                        
                        st.success(f"✅ Consulta de {animal} registrada com sucesso!")
                        st.balloons()
                        
                        # Sugerir agendamento de retorno
                        if retorno > 0:
                            data_retorno = data_consulta + pd.Timedelta(days=retorno)
                            st.info(f"📅 Lembrete: Agendar retorno para {data_retorno.strftime('%d/%m/%Y')}")
        else:
            st.warning("Cadastre um animal primeiro!")
    
    with tab2:
        st.subheader("📋 Histórico de Consultas")
        if st.session_state.historico_consultas:
            df_hist = pd.DataFrame(st.session_state.historico_consultas)
            st.dataframe(df_hist[['Data', 'Animal', 'Dono', 'A_Diagnostico']], use_container_width=True)
            
            # Busca avançada
            st.subheader("Buscar Consultas")
            busca = st.text_input("Digite animal, dono ou diagnóstico")
            if busca:
                resultados = df_hist[
                    df_hist['Animal'].str.contains(busca, case=False, na=False) |
                    df_hist['Dono'].str.contains(busca, case=False, na=False) |
                    df_hist['A_Diagnostico'].str.contains(busca, case=False, na=False)
                ]
                st.write(f"Encontradas: {len(resultados)}")
                st.dataframe(resultados)
        else:
            st.info("Nenhuma consulta registrada")
    
    with tab3:
        st.subheader("🔍 Anamnese Rápida")
        st.markdown("""
        <div class="card">
            <h4>Checklist de Anamnese</h4>
            <p>Use este guia rápido para não esquecer nenhum ponto importante</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Sistema Respiratório**")
            st.checkbox("Tosse")
            st.checkbox("Espirros")
            st.checkbox("Secreção nasal")
            st.checkbox("Dificuldade respiratória")
            
            st.markdown("**Sistema Digestivo**")
            st.checkbox("Vômito")
            st.checkbox("Diarreia")
            st.checkbox("Falta de apetite")
            st.checkbox("Disfagia")
            
            st.markdown("**Sistema Urinário**")
            st.checkbox("Poliúria")
            st.checkbox("Disúria")
            st.checkbox("Hematúria")
        
        with col2:
            st.markdown("**Sistema Tegumentar**")
            st.checkbox("Prurido")
            st.checkbox("Queda de pelo")
            st.checkbox("Lesões de pele")
            st.checkbox("Descamação")
            
            st.markdown("**Olhos e Ouvidos**")
            st.checkbox("Secreção ocular")
            st.checkbox("Vermelhidão")
            st.checkbox("Coceira nos ouvidos")
            st.checkbox("Odor nos ouvidos")
            
            st.markdown("**Sistema Nervoso**")
            st.checkbox("Convulsões")
            st.checkbox("Tremores")
            st.checkbox("Alteração de comportamento")

elif opcao == "📜 PRONTUÁRIO":
    st.title("📜 Prontuário Eletrônico")
    
    if not df_pets.empty:
        # Selecionar animal
        animal = st.selectbox("Selecione o animal", df_pets['Pet'].tolist())
        
        if animal:
            # Buscar dados do animal
            dados_animal = df_pets[df_pets['Pet'] == animal].iloc[0]
            
            # Informações básicas
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"""
                ### 🐕 Dados do Paciente
                **Nome:** {dados_animal['Pet']}  
                **Espécie:** {dados_animal['Especie']}  
                **Raça:** {dados_animal.get('Raca', 'N/I')}  
                **Sexo:** {dados_animal.get('Sexo', 'N/I')}  
                **Idade:** {dados_animal.get('Idade', 'N/I')}  
                **Peso:** {dados_animal.get('Peso', 'N/I')} kg
                """)
            
            with col2:
                st.markdown(f"""
                ### 👤 Proprietário
                **Nome:** {dados_animal['Dono']}  
                **Alergias:** {dados_animal.get('Alergias', 'N/I')}  
                **Microchip:** {dados_animal.get('Microchip', 'N/I')}
                """)
            
            st.markdown("---")
            
            # Histórico de consultas
            st.subheader("📋 Histórico de Consultas")
            
            if animal in st.session_state.prontuarios and st.session_state.prontuarios[animal]:
                for i, consulta in enumerate(st.session_state.prontuarios[animal][::-1]):  # Mais recentes primeiro
                    with st.expander(f"Consulta {i+1} - {consulta['Data']} - {consulta['A_Diagnostico'][:50]}..."):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("**Subjetivo (S)**")
                            st.write(consulta['S_Queixa'])
                            if consulta.get('S_Historico'):
                                st.write("Histórico:", consulta['S_Historico'])
                            
                            st.markdown("**Avaliação (A)**")
                            st.write(consulta['A_Diagnostico'])
                        
                        with col2:
                            st.markdown("**Objetivo (O)**")
                            st.write(f"Temp: {consulta.get('O_Temperatura', 'N/I')}°C")
                            st.write(f"FC: {consulta.get('O_FC', 'N/I')} bpm")
                            st.write(f"FR: {consulta.get('O_FR', 'N/I')} mpm")
                            st.write(f"Mucosas: {consulta.get('O_Mucosa', 'N/I')}")
                        
                        st.markdown("**Plano (P)**")
                        if consulta.get('P_Tratamento'):
                            st.write("Tratamento:", consulta['P_Tratamento'])
                        if consulta.get('P_Exames'):
                            st.write("Exames:", consulta['P_Exames'])
                        if consulta.get('P_Orientacoes'):
                            st.write("Orientações:", consulta['P_Orientacoes'])
                        
                        # Botão para gerar receita a partir da consulta
                        if st.button(f"💊 Gerar Receita desta Consulta", key=f"rec_{i}"):
                            st.session_state['receita_temp'] = {
                                'proprietario': dados_animal['Dono'],
                                'animal': animal,
                                'especie': dados_animal['Especie'],
                                'medicamento': "Conforme prescrição",
                                'posologia': consulta.get('P_Tratamento', ''),
                                'diagnostico': consulta.get('A_Diagnostico', '')
                            }
                            st.success("Dados carregados! Vá para o módulo de Receituário.")
            else:
                st.info("Nenhuma consulta registrada para este animal")
            
            # Botão para gerar prontuário completo em PDF
            if st.button("📄 GERAR PRONTUÁRIO COMPLETO PDF", use_container_width=True):
                st.info("Funcionalidade de PDF será implementada na próxima versão")
    else:
        st.warning("Cadastre um animal primeiro!")

elif opcao == "💊 RECEITUÁRIO":
    st.title("💊 Receituário Veterinário")
    
    tab1, tab2 = st.tabs(["📝 Nova Receita", "📋 Receitas Anteriores"])
    
    with tab1:
        st.markdown("""
        <div class="receita">
            <h3 style="text-align: center;">RECEITUÁRIO VETERINÁRIO</h3>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("form_receita"):
            col1, col2 = st.columns(2)
            
            with col1:
                # Dados do proprietário
                if not df_tutores.empty:
                    proprietario = st.selectbox("Proprietário *", df_tutores['Nome'].tolist())
                else:
                    st.error("Cadastre um cliente primeiro!")
                    proprietario = None
                
                # Dados do animal
                if not df_pets.empty:
                    # Filtrar animais do proprietário selecionado
                    animais_proprietario = df_pets[df_pets['Dono'] == proprietario]['Pet'].tolist() if proprietario else []
                    animal = st.selectbox("Animal *", animais_proprietario if animais_proprietario else ["Nenhum"])
                else:
                    st.error("Cadastre um animal primeiro!")
                    animal = None
            
            with col2:
                especie = st.text_input("Espécie", value=df_pets[df_pets['Pet'] == animal]['Especie'].iloc[0] if animal in df_pets['Pet'].values else "")
                data = st.date_input("Data", datetime.now())
            
            st.markdown("---")
            
            # Dados da receita
            st.subheader("Medicação Prescrita")
            
            medicamento = st.text_input("Medicamento *")
            apresentacao = st.text_input("Apresentação (ex: comprimidos 100mg, solução 10ml)")
            posologia = st.text_area("Posologia *", placeholder="Ex: 1 comprimido a cada 12 horas por 7 dias")
            duracao = st.text_input("Duração do tratamento")
            observacoes = st.text_area("Observações adicionais")
            
            # Diagnóstico associado
            st.subheader("Diagnóstico")
            diagnostico = st.text_area("Diagnóstico / CID")
            
            col1, col2, col3 = st.columns(3)
            with col2:
                submitted = st.form_submit_button("📄 GERAR RECEITA", use_container_width=True)
            
            if submitted and proprietario and animal and medicamento and posologia:
                dados_receita = {
                    'proprietario': proprietario,
                    'animal': animal,
                    'especie': especie,
                    'medicamento': medicamento,
                    'apresentacao': apresentacao,
                    'posologia': posologia,
                    'duracao': duracao,
                    'observacoes': observacoes,
                    'diagnostico': diagnostico,
                    'data': data.strftime('%d/%m/%Y')
                }
                
                # Gerar PDF
                pdf_path = criar_pdf_receita(dados_receita)
                
                with open(pdf_path, "rb") as pdf_file:
                    pdf_data = pdf_file.read()
                
                st.success("✅ Receita gerada com sucesso!")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Botão para download
                    st.download_button(
                        label="📥 BAIXAR RECEITA PDF",
                        data=pdf_data,
                        file_name=f"receita_{animal}_{data.strftime('%Y%m%d')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                
                with col2:
                    # Compartilhar WhatsApp
                    if proprietario:
                        telefone = df_tutores[df_tutores['Nome'] == proprietario]['WhatsApp'].iloc[0]
                        mensagem = f"*RECEITA VETERINÁRIA*\n\nAnimal: {animal}\nMedicamento: {medicamento}\nPosologia: {posologia}\nData: {data.strftime('%d/%m/%Y')}"
                        link = enviar_whatsapp(mensagem, telefone)
                        st.markdown(f"[📱 ENVIAR POR WHATSAPP]({link})")
                
                # Limpar arquivo temporário
                os.unlink(pdf_path)
            elif submitted:
                st.error("Preencha os campos obrigatórios!")
    
    with tab2:
        st.subheader("Receitas Emitidas")
        st.info("Histórico de receitas será implementado na próxima versão")

elif opcao == "📚 BULAS":
    st.title("📚 Consulta de Bulas Veterinárias")
    
    st.markdown("""
    <div class="card">
        <h4>Base de dados de medicamentos veterinários</h4>
        <p>Consulte informações completas sobre princípios ativos, dosagens e indicações.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Busca de medicamentos
    col1, col2 = st.columns([3, 1])
    
    with col1:
        busca = st.text_input("🔍 Buscar medicamento", placeholder="Digite o nome do princípio ativo...")
    
    with col2:
        st.markdown("###")
        if st.button("Limpar busca"):
            busca = ""
            st.rerun()
    
    # Lista de medicamentos disponíveis
    medicamentos = list(st.session_state.medicamentos_db.keys())
    
    # Filtrar por busca
    if busca:
        medicamentos_filtrados = [m for m in medicamentos if busca.lower() in m.lower()]
    else:
        medicamentos_filtrados = medicamentos
    
    if medicamentos_filtrados:
        # Selecionar medicamento
        medicamento_sel = st.selectbox("Selecione o medicamento", medicamentos_filtrados)
        
        if medicamento_sel:
            dados = st.session_state.medicamentos_db[medicamento_sel]
            
            # Exibir informações em cards
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"""
                <div class="card">
                    <h4 style="color: #2196F3;">📋 Informações Básicas</h4>
                    <p><strong>Medicamento:</strong> {medicamento_sel}</p>
                    <p><strong>Apresentação:</strong> {dados['apresentacao']}</p>
                    <p><strong>Via de Administração:</strong> {dados['via']}</p>
                </div>
                
                <div class="card">
                    <h4 style="color: #4CAF50;">💊 Indicações</h4>
                    <p>{dados['indicacao']}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="card">
                    <h4 style="color: #FF9800;">⚕️ Dosagem</h4>
                    <p><strong>Dosagem recomendada:</strong> {dados['dosagem']}</p>
                </div>
                
                <div class="card">
                    <h4 style="color: #f44336;">⚠️ Contraindicações</h4>
                    <p>{dados['contraindicacoes']}</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Bula completa
            with st.expander("📖 Ver bula completa"):
                st.markdown(f"""
                **Bula do {medicamento_sel}**  
                
                {dados['bula']}
                
                ---
                
                **Farmacocinética:**  
                Medicamento de uso veterinário. Consulte um médico veterinário antes de administrar.
                
                **Armazenamento:**  
                Manter em temperatura ambiente, protegido da luz e umidade.
                
                **Descarte:**  
                Não descartar em esgoto doméstico. Seguir orientações do fabricante.
                """)
            
            # Botão para incluir na receita
            if st.button(f"➕ Usar {medicamento_sel} em nova receita", use_container_width=True):
                st.session_state['receita_temp'] = {
                    'medicamento': medicamento_sel,
                    'apresentacao': dados['apresentacao']
                }
                st.success("Medicamento selecionado! Vá para o módulo de Receituário.")
    else:
        st.warning("Nenhum medicamento encontrado")

elif opcao == "💰 FINANCEIRO":
    st.title("💰 Gestão Financeira")
    
    tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "💰 Receitas", "📝 Despesas"])
    
    with tab1:
        st.subheader("Resumo Financeiro")
        
        # Métricas financeiras
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_consultas = len(st.session_state.historico_consultas)
            receita_total = total_consultas * 150
            st.metric("Receita Total", f"R$ {receita_total:,.2f}")
        
        with col2:
            # Calcular consultas do mês
            consultas_mes = len([c for c in st.session_state.historico_consultas 
                               if c['Data'][3:5] == datetime.now().strftime('%m')])
            receita_mes = consultas_mes * 150
            st.metric("Receita do Mês", f"R$ {receita_mes:,.2f}")
        
        with col3:
            ticket_medio = receita_total / total_consultas if total_consultas > 0 else 0
            st.metric("Ticket Médio", f"R$ {ticket_medio:,.2f}")
        
        with col4:
            st.metric("Consultas Realizadas", total_consultas)
        
        # Gráfico de receitas
        if st.session_state.historico_consultas:
            df_receitas = pd.DataFrame(st.session_state.historico_consultas)
            df_receitas['Data'] = pd.to_datetime(df_receitas['Data'], format='%d/%m/%Y')
            df_receitas['Mês'] = df_receitas['Data'].dt.month
            receitas_por_mes = df_receitas.groupby('Mês').size() * 150
            
            fig = px.line(x=receitas_por_mes.index, y=receitas_por_mes.values,
                         labels={'x':'Mês', 'y':'Receita (R$)'},
                         title="Evolução da Receita")
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("Registro de Receitas")
        
        with st.form("form_receita_financeira"):
            col1, col2 = st.columns(2)
            
            with col1:
                data = st.date_input("Data", datetime.now())
                if not df_tutores.empty:
                    cliente = st.selectbox("Cliente", df_tutores['Nome'].tolist())
                else:
                    cliente = st.text_input("Cliente")
            
            with col2:
                valor = st.number_input("Valor (R$)", min_value=0.0, step=10.0)
                forma_pagto = st.selectbox("Forma de Pagamento", 
                                          ["Dinheiro", "Cartão Crédito", "Cartão Débito", "Pix", "Transferência"])
            
            descricao = st.text_area("Descrição/Serviço")
            
            if st.form_submit_button("Registrar Receita"):
                st.success("Receita registrada com sucesso!")
    
    with tab3:
        st.subheader("Registro de Despesas")
        st.info("Módulo de despesas em desenvolvimento")

elif opcao == "📅 AGENDA":
    st.title("📅 Agenda de Consultas")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Calendário")
        
        # Selecionar data
        data_agenda = st.date_input("Selecionar data", datetime.now())
        
        # Mostrar consultas do dia
        st.subheader(f"Consultas de {data_agenda.strftime('%d/%m/%Y')}")
        
        consultas_dia = [a for a in st.session_state.agendamentos 
                        if a.get('Data') == data_agenda.strftime('%d/%m/%Y')]
        
        if consultas_dia:
            for consulta in consultas_dia:
                with st.container():
                    col_a, col_b, col_c = st.columns([2, 2, 1])
                    with col_a:
                        st.write(f"🕐 {consulta.get('Hora', '--:--')}")
                    with col_b:
                        st.write(f"🐕 {consulta.get('Animal', 'N/I')}")
                    with col_c:
                        st.write(f"👤 {consulta.get('Cliente', 'N/I')}")
                    st.divider()
        else:
            st.info("Nenhuma consulta agendada para esta data")
    
    with col2:
        st.subheader("Novo Agendamento")
        
        with st.form("form_agenda"):
            data = st.date_input("Data", min_value=datetime.now().date())
            hora = st.time_input("Horário")
            
            if not df_tutores.empty:
                cliente = st.selectbox("Cliente", df_tutores['Nome'].tolist())
                
                # Filtrar pets do cliente
                pets_cliente = df_pets[df_pets['Dono'] == cliente]['Pet'].tolist()
                if pets_cliente:
                    animal = st.selectbox("Animal", pets_cliente)
                else:
                    animal = st.text_input("Animal (nenhum cadastrado)")
                    st.warning("Este cliente não tem animais cadastrados")
            else:
                cliente = st.text_input("Cliente")
                animal = st.text_input("Animal")
            
            tipo = st.selectbox("Tipo", ["Consulta", "Retorno", "Vacina", "Cirurgia", "Exame"])
            observacoes = st.text_area("Observações")
            
            if st.form_submit_button("Agendar"):
                agendamento = {
                    "Data": data.strftime('%d/%m/%Y'),
                    "Hora": hora.strftime('%H:%M'),
                    "Cliente": cliente,
                    "Animal": animal,
                    "Tipo": tipo,
                    "Observacoes": observacoes,
                    "Status": "Agendado"
                }
                st.session_state.agendamentos.append(agendamento)
                st.success("Agendamento realizado!")
                st.rerun()

# Rodapé
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col2:
    st.caption("🐾 Ribeira Vet Pro v24.0 - Sistema Completo de Gestão Veterinária")
    st.caption("Desenvolvido com 💙 para Médicos Veterinários")
