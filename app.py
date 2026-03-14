import streamlit as st
import pandas as pd
import os
from datetime import datetime
import zipfile
import io

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
    
    /* Cards para estatísticas */
    .stat-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# 2. INICIALIZAÇÃO DO ESTADO DA SESSÃO
if 'form_data' not in st.session_state:
    st.session_state.form_data = {}
if 'editando' not in st.session_state:
    st.session_state.editando = None
if 'confirmar_exclusao' not in st.session_state:
    st.session_state.confirmar_exclusao = False
if 'historico' not in st.session_state:
    st.session_state.historico = []
if 'excluir_idx' not in st.session_state:
    st.session_state.excluir_idx = None

# 3. FUNÇÕES UTILITÁRIAS
def formatar_cpf(cpf):
    """Aplica máscara de CPF: 000.000.000-00"""
    if pd.isna(cpf) or cpf == "":
        return ""
    cpf = ''.join(filter(str.isdigit, str(cpf)))
    if len(cpf) == 11:
        return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
    return cpf

def formatar_telefone(telefone):
    """Aplica máscara de telefone: (00) 00000-0000"""
    if pd.isna(telefone) or telefone == "":
        return ""
    telefone = ''.join(filter(str.isdigit, str(telefone)))
    if len(telefone) == 11:
        return f"({telefone[:2]}) {telefone[2:7]}-{telefone[7:]}"
    elif len(telefone) == 10:
        return f"({telefone[:2]}) {telefone[2:6]}-{telefone[6:]}"
    return telefone

def validar_cpf_unico(cpf, df, ignore_index=None):
    """Valida se CPF é único"""
    if cpf in df['CPF'].values:
        if ignore_index is not None and df.iloc[ignore_index]['CPF'] == cpf:
            return True
        return False
    return True

def salvar_dados_com_seguranca(df, nome_arquivo):
    """Salva dados com tratamento de erro"""
    try:
        df.to_csv(nome_arquivo, index=False)
        return True
    except Exception as e:
        st.error(f"Erro ao salvar dados: {e}")
        return False

def carregar_dados(arquivo, colunas):
    """Carrega dados do arquivo CSV"""
    if os.path.exists(arquivo):
        try:
            return pd.read_csv(arquivo)
        except:
            return pd.DataFrame(columns=colunas)
    return pd.DataFrame(columns=colunas)

def gerar_recibo_profissional(nome, servico, valor):
    """Gera recibo em formato HTML"""
    data_atual = datetime.now().strftime('%d/%m/%Y %H:%M')
    recibo_html = f"""
    <div style="border: 2px solid #333; padding: 30px; max-width: 500px; margin: 0 auto; 
                font-family: Arial, sans-serif; background-color: white; border-radius: 10px;
                box-shadow: 5px 5px 15px rgba(0,0,0,0.2);">
        <h2 style="text-align: center; color: #2c3e50; margin-bottom: 30px;">🐾 RECIBO VETERINÁRIO</h2>
        <p style="font-size: 16px; margin: 15px 0;"><strong>Recebemos de:</strong> {nome}</p>
        <p style="font-size: 16px; margin: 15px 0;"><strong>Referente a:</strong> {servico}</p>
        <p style="font-size: 16px; margin: 15px 0;"><strong>Valor:</strong> R$ {valor}</p>
        <hr style="margin: 25px 0;">
        <p style="font-size: 14px; color: #666; text-align: right;">São Paulo, {data_atual}</p>
        <p style="font-size: 14px; color: #666; text-align: center; margin-top: 40px;">
            _________________________<br>
            Assinatura do Responsável
        </p>
    </div>
    """
    return recibo_html

# 4. CARREGAR BASES DE DADOS
df_tutores = carregar_dados('tutores_v23.csv', ["Nome", "CPF", "WhatsApp", "Email", "Endereco"])
df_pets = carregar_dados('pets_v23.csv', ["Dono", "Pet", "Especie", "Raca", "Peso", "Idade"])

# 5. MENU LATERAL COM ESTATÍSTICAS
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2138/2138440.png", width=80)
    st.title("🐕 Menu Principal")
    
    opcao = st.radio("Selecione uma página:", 
                     ["📊 Dashboard", "👤 Cadastro de Clientes", "🐾 Cadastro de Animais", 
                      "💰 Financeiro e Recibos", "📅 Agendamentos", "📈 Histórico"])
    
    st.divider()
    
    # Estatísticas rápidas na sidebar
    st.subheader("📊 Estatísticas Rápidas")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Clientes", len(df_tutores))
    with col2:
        st.metric("Animais", len(df_pets))
    
    if not df_pets.empty:
        caes = len(df_pets[df_pets['Especie'] == 'Cão'])
        gatos = len(df_pets[df_pets['Especie'] == 'Gato'])
        st.write(f"🐕 Cães: {caes}")
        st.write(f"🐈 Gatos: {gatos}")
    
    st.divider()
    
    # Backup na sidebar
    if st.button("💾 Criar Backup"):
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            with zipfile.ZipFile(f"backup_{timestamp}.zip", 'w') as zipf:
                if os.path.exists('tutores_v23.csv'):
                    zipf.write('tutores_v23.csv')
                if os.path.exists('pets_v23.csv'):
                    zipf.write('pets_v23.csv')
            st.success(f"Backup criado: backup_{timestamp}.zip")
        except Exception as e:
            st.error(f"Erro ao criar backup: {e}")
    
    st.info("Versão 23.0 - Registro Seguro")

# 6. PÁGINAS DO SISTEMA

if opcao == "📊 Dashboard":
    st.header("📊 Dashboard da Clínica")
    
    # Métricas principais em cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""
        <div class="stat-card">
            <h3>👥 Clientes</h3>
            <h2>{}</h2>
        </div>
        """.format(len(df_tutores)), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="stat-card">
            <h3>🐕 Animais</h3>
            <h2>{}</h2>
        </div>
        """.format(len(df_pets)), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="stat-card">
            <h3>📅 Consultas</h3>
            <h2>{}</h2>
        </div>
        """.format(len(st.session_state.historico)), unsafe_allow_html=True)
    
    with col4:
        valor_total = len(st.session_state.historico) * 150
        st.markdown("""
        <div class="stat-card">
            <h3>💰 Faturamento</h3>
            <h2>R$ {}</h2>
        </div>
        """.format(valor_total), unsafe_allow_html=True)
    
    # Gráficos simples
    st.subheader("📈 Distribuição de Animais")
    if not df_pets.empty:
        especies = df_pets['Especie'].value_counts()
        st.bar_chart(especies)
    else:
        st.info("Nenhum animal cadastrado ainda.")

elif opcao == "👤 Cadastro de Clientes":
    st.header("👤 Gestão de Clientes")
    
    # Formulário de cadastro/edição
    with st.form("form_tutor", clear_on_submit=False):
        st.subheader("✏️ {} Cliente".format("Editar" if st.session_state.editando else "Novo"))
        
        # Carregar dados para edição se existirem
        valor_nome = st.session_state.editando.get('Nome', '') if st.session_state.editando else ''
        valor_cpf = st.session_state.editando.get('CPF', '') if st.session_state.editando else ''
        valor_whats = st.session_state.editando.get('WhatsApp', '') if st.session_state.editando else ''
        valor_email = st.session_state.editando.get('Email', '') if st.session_state.editando else ''
        valor_end = st.session_state.editando.get('Endereco', '') if st.session_state.editando else ''
        
        c1, c2 = st.columns(2)
        n = c1.text_input("Nome do Cliente *", value=valor_nome)
        c = c2.text_input("CPF *", value=valor_cpf, help="Digite apenas números")
        w = c1.text_input("WhatsApp *", value=valor_whats, help="Digite apenas números")
        e = c2.text_input("E-mail", value=valor_email)
        end = st.text_input("Endereço Completo", value=valor_end)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            submit = st.form_submit_button("💾 SALVAR CLIENTE")
        with col2:
            if st.session_state.editando:
                cancelar = st.form_submit_button("❌ Cancelar Edição")
        
        if submit:
            # Validações
            if not n or not c or not w:
                st.error("Preencha os campos obrigatórios (*)!")
            else:
                # Verificar CPF duplicado
                idx_ignore = None
                if st.session_state.editando:
                    idx_ignore = df_tutores[df_tutores['CPF'] == st.session_state.editando['CPF']].index[0]
                
                if validar_cpf_unico(c, df_tutores, idx_ignore):
                    if st.session_state.editando:
                        # Atualizar registro existente
                        df_tutores.loc[idx_ignore] = [n, c, w, e, end]
                        if salvar_dados_com_seguranca(df_tutores, 'tutores_v23.csv'):
                            st.success("Cliente atualizado com sucesso!")
                            st.session_state.editando = None
                            st.rerun()
                    else:
                        # Novo registro
                        novo_t = pd.DataFrame([{"Nome": n, "CPF": c, "WhatsApp": w, "Email": e, "Endereco": end}])
                        novo_t.to_csv('tutores_v23.csv', mode='a', header=not os.path.exists('tutores_v23.csv'), index=False)
                        st.success("Cliente salvo com sucesso!")
                        st.rerun()
                else:
                    st.error("CPF já cadastrado!")
        
        if st.session_state.editando and 'cancelar' in locals() and cancelar:
            st.session_state.editando = None
            st.rerun()
    
    st.divider()
    
    # Lista de clientes com opções de editar/excluir
    st.subheader("📋 Clientes Cadastrados")
    
    # Barra de pesquisa
    termo_busca = st.text_input("🔍 Pesquisar clientes:", placeholder="Digite nome ou CPF...")
    
    if not df_tutores.empty:
        # Filtrar dados
        df_display = df_tutores.copy()
        df_display['CPF'] = df_display['CPF'].apply(formatar_cpf)
        df_display['WhatsApp'] = df_display['WhatsApp'].apply(formatar_telefone)
        
        if termo_busca:
            df_display = df_display[
                df_display['Nome'].str.contains(termo_busca, case=False, na=False) |
                df_display['CPF'].str.contains(termo_busca, na=False)
            ]
        
        # Exibir tabela com botões
        for idx, row in df_display.iterrows():
            with st.container():
                col1, col2, col3, col4 = st.columns([4, 1, 1, 1])
                with col1:
                    st.write(f"**{row['Nome']}** - CPF: {row['CPF']} - Tel: {row['WhatsApp']}")
                with col2:
                    if st.button(f"📝 Editar", key=f"edit_{idx}"):
                        # Encontrar o índice original no df_tutores
                        idx_original = df_tutores[df_tutores['CPF'] == row['CPF'].replace('.', '').replace('-', '')].index
                        if len(idx_original) > 0:
                            st.session_state.editando = df_tutores.iloc[idx_original[0]].to_dict()
                            st.rerun()
                with col3:
                    if st.button(f"🗑️ Excluir", key=f"del_{idx}"):
                        st.session_state.confirmar_exclusao = True
                        st.session_state.excluir_idx = idx_original[0]
                with col4:
                    if st.button(f"🐕 Pets", key=f"pets_{idx}"):
                        st.session_state['ver_pets'] = row['Nome']
                st.divider()
        
        # Confirmação de exclusão
        if st.session_state.confirmar_exclusao:
            st.warning("⚠️ Tem certeza que deseja excluir este cliente?")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Sim, excluir"):
                    df_tutores = df_tutores.drop(st.session_state.excluir_idx).reset_index(drop=True)
                    if salvar_dados_com_seguranca(df_tutores, 'tutores_v23.csv'):
                        st.success("Cliente excluído com sucesso!")
                        st.session_state.confirmar_exclusao = False
                        st.rerun()
            with col2:
                if st.button("❌ Cancelar"):
                    st.session_state.confirmar_exclusao = False
                    st.rerun()
    else:
        st.info("Nenhum cliente cadastrado ainda.")

elif opcao == "🐾 Cadastro de Animais":
    st.header("🐾 Gestão de Animais")
    
    # Ver pets de um cliente específico
    if 'ver_pets' in st.session_state:
        st.info(f"Mostrando animais de: **{st.session_state['ver_pets']}**")
        if st.button("Voltar para lista completa"):
            del st.session_state['ver_pets']
            st.rerun()
    
    with st.form("form_pet", clear_on_submit=False):
        st.subheader("✏️ Novo Animal")
        
        # Busca lista de donos para o selectbox
        lista_donos = ["Selecione um dono..."] + df_tutores['Nome'].tolist() if not df_tutores.empty else ["Nenhum cliente cadastrado"]
        dono_sel = st.selectbox("Dono do Animal *", lista_donos)
        
        c1, c2 = st.columns(2)
        p_nome = c1.text_input("Nome do Pet *")
        p_esp = c2.selectbox("Espécie *", ["Cão", "Gato", "Ave", "Outro"])
        p_raca = c1.text_input("Raça")
        p_idade = c2.text_input("Idade")
        p_peso = st.text_input("Peso (kg)")
        
        if st.form_submit_button("💾 SALVAR ANIMAL"):
            if dono_sel == "Selecione um dono..." or dono_sel == "Nenhum cliente cadastrado":
                st.error("Selecione um dono válido!")
            elif not p_nome:
                st.error("Digite o nome do animal!")
            else:
                novo_p = pd.DataFrame([{
                    "Dono": dono_sel, 
                    "Pet": p_nome, 
                    "Especie": p_esp, 
                    "Raca": p_raca, 
                    "Peso": p_peso, 
                    "Idade": p_idade
                }])
                novo_p.to_csv('pets_v23.csv', mode='a', header=not os.path.exists('pets_v23.csv'), index=False)
                st.success(f"O animal {p_nome} foi registrado!")
                st.rerun()
    
    st.divider()
    
    # Lista de animais
    st.subheader("📋 Lista de Animais Cadastrados")
    
    # Filtros
    col1, col2 = st.columns(2)
    with col1:
        filtro_especie = st.selectbox("Filtrar por espécie:", ["Todos", "Cão", "Gato", "Ave", "Outro"])
    with col2:
        if 'ver_pets' in st.session_state:
            filtro_dono = st.session_state['ver_pets']
        else:
            filtro_dono = st.selectbox("Filtrar por dono:", ["Todos"] + df_tutores['Nome'].tolist())
    
    # Aplicar filtros
    df_pets_display = df_pets.copy()
    if filtro_especie != "Todos":
        df_pets_display = df_pets_display[df_pets_display['Especie'] == filtro_especie]
    if filtro_dono != "Todos" and filtro_dono != "Selecione um dono...":
        df_pets_display = df_pets_display[df_pets_display['Dono'] == filtro_dono]
    
    if not df_pets_display.empty:
        st.dataframe(df_pets_display, use_container_width=True)
    else:
        st.info("Nenhum animal encontrado com os filtros selecionados.")

elif opcao == "💰 Financeiro e Recibos":
    st.header("💰 Financeiro")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 Tabela de Preços")
        precos = pd.DataFrame({
            "Serviço": ["Consulta", "Vacina V10", "Vacina Antirrábica", "Castração", "Banho e Tosa", "Ultrassom"],
            "Valor": ["R$ 150,00", "R$ 130,00", "R$ 80,00", "R$ 450,00", "R$ 120,00", "R$ 300,00"]
        })
        st.table(precos)
        
        # Estatísticas financeiras
        st.subheader("📊 Resumo Financeiro")
        total_consultas = len([h for h in st.session_state.historico if 'consulta' in h.get('Observações', '').lower()])
        faturamento_estimado = total_consultas * 150
        st.metric("Faturamento Estimado", f"R$ {faturamento_estimado:,.2f}")
    
    with col2:
        st.subheader("📄 Emissão de Recibo")
        
        # Sugestões baseadas em dados existentes
        sugestao_cliente = st.selectbox("Cliente (opcional)", ["Selecione..."] + df_tutores['Nome'].tolist())
        sugestao_servico = st.selectbox("Serviço (opcional)", ["Selecione..."] + precos['Serviço'].tolist())
        
        r_nome = st.text_input("Nome do Cliente *", 
                               value=sugestao_cliente if sugestao_cliente != "Selecione..." else "")
        r_serv = st.text_input("Serviço Realizado *",
                               value=sugestao_servico if sugestao_servico != "Selecione..." else "")
        r_valor = st.text_input("Valor (R$) *")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📝 GERAR RECIBO"):
                if r_nome and r_serv and r_valor:
                    recibo_html = gerar_recibo_profissional(r_nome, r_serv, r_valor)
                    st.session_state['ultimo_recibo'] = recibo_html
                    st.success("Recibo gerado com sucesso!")
                else:
                    st.error("Preencha todos os campos obrigatórios!")
        
        with col2:
            if st.button("📋 COPIAR RECIBO"):
                if 'ultimo_recibo' in st.session_state:
                    st.info("Recibo pronto para copiar!")
        
        # Exibir último recibo
        if 'ultimo_recibo' in st.session_state:
            st.divider()
            st.subheader("📎 Recibo Gerado")
            st.markdown(st.session_state['ultimo_recibo'], unsafe_allow_html=True)

elif opcao == "📅 Agendamentos":
    st.header("📅 Agendamento de Consultas")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Novo Agendamento")
        
        if not df_tutores.empty and not df_pets.empty:
            with st.form("form_agendamento"):
                data_consulta = st.date_input("Data da Consulta", min_value=datetime.now().date())
                hora_consulta = st.time_input("Horário")
                
                cliente_consulta = st.selectbox("Cliente", df_tutores['Nome'].tolist())
                
                # Filtrar pets do cliente selecionado
                pets_cliente = df_pets[df_pets['Dono'] == cliente_consulta]['Pet'].tolist()
                if pets_cliente:
                    pet_consulta = st.selectbox("Animal", pets_cliente)
                else:
                    st.warning("Este cliente não possui animais cadastrados!")
                    pet_consulta = None
                
                tipo_consulta = st.selectbox("Tipo de Consulta", 
                                            ["Consulta Rotina", "Vacinação", "Emergência", "Retorno", "Cirurgia"])
                observacoes = st.text_area("Observações")
                
                if st.form_submit_button("📅 AGENDAR"):
                    if pet_consulta:
                        agendamento = {
                            "Data": data_consulta.strftime('%d/%m/%Y'),
                            "Hora": hora_consulta.strftime('%H:%M'),
                            "Cliente": cliente_consulta,
                            "Animal": pet_consulta,
                            "Tipo": tipo_consulta,
                            "Observações": observacoes,
                            "Status": "Agendado"
                        }
                        
                        if 'agendamentos' not in st.session_state:
                            st.session_state.agendamentos = []
                        
                        st.session_state.agendamentos.append(agendamento)
                        st.success("Consulta agendada com sucesso!")
                    else:
                        st.error("Selecione um animal para a consulta!")
        else:
            st.warning("Cadastre clientes e animais antes de fazer agendamentos!")
    
    with col2:
        st.subheader("Próximas Consultas")
        
        if 'agendamentos' in st.session_state and st.session_state.agendamentos:
            df_agendamentos = pd.DataFrame(st.session_state.agendamentos)
            df_agendamentos = df_agendamentos.sort_values(['Data', 'Hora'])
            st.dataframe(df_agendamentos, use_container_width=True)
            
            # Opção para cancelar agendamento
            st.subheader("Cancelar Agendamento")
            agendamento_sel = st.selectbox(
                "Selecione o agendamento para cancelar:",
                [f"{a['Data']} {a['Hora']} - {a['Cliente']} - {a['Animal']}" 
                 for a in st.session_state.agendamentos]
            )
            
            if st.button("❌ Cancelar Agendamento"):
                idx = [f"{a['Data']} {a['Hora']} - {a['Cliente']} - {a['Animal']}" 
                      for a in st.session_state.agendamentos].index(agendamento_sel)
                st.session_state.agendamentos.pop(idx)
                st.success("Agendamento cancelado!")
                st.rerun()
        else:
            st.info("Nenhum agendamento futuro.")

elif opcao == "📈 Histórico":
    st.header("📈 Histórico de Atendimentos")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Registrar Novo Atendimento")
        
        if not df_pets.empty:
            with st.form("form_historico"):
                pet_atendimento = st.selectbox("Selecione o animal", df_pets['Pet'].tolist())
                
                # Mostrar dono do animal selecionado
                dono_pet = df_pets[df_pets['Pet'] == pet_atendimento]['Dono'].iloc[0]
                st.info(f"Dono: {dono_pet}")
                
                data_atendimento = st.date_input("Data do atendimento", datetime.now())
                tipo_atendimento = st.selectbox("Tipo de Atendimento", 
                                               ["Consulta", "Vacina", "Cirurgia", "Retorno", "Emergência"])
                valor_atendimento = st.number_input("Valor (R$)", min_value=0.0, step=10.0)
                observacoes = st.text_area("Observações", height=100)
                
                if st.form_submit_button("📝 REGISTRAR ATENDIMENTO"):
                    atendimento = {
                        "Animal": pet_atendimento,
                        "Dono": dono_pet,
                        "Data": data_atendimento.strftime('%d/%m/%Y'),
                        "Tipo": tipo_atendimento,
                        "Valor": f"R$ {valor_atendimento:.2f}",
                        "Observações": observacoes
                    }
                    st.session_state.historico.append(atendimento)
                    st.success("Atendimento registrado com sucesso!")
                    st.rerun()
        else:
            st.warning("Cadastre animais primeiro!")
    
    with col2:
        st.subheader("Filtros")
        if st.session_state.historico:
            filtro_animal = st.selectbox("Filtrar por animal:", 
                                        ["Todos"] + list(set([h['Animal'] for h in st.session_state.historico])))
            filtro_tipo = st.selectbox("Filtrar por tipo:", 
                                      ["Todos"] + list(set([h['Tipo'] for h in st.session_state.historico])))
        else:
            filtro_animal = "Todos"
            filtro_tipo = "Todos"
    
    st.divider()
    
    # Exibir histórico
    st.subheader("📋 Histórico Completo")
    
    if st.session_state.historico:
        df_historico = pd.DataFrame(st.session_state.historico)
        
        # Aplicar filtros
        if filtro_animal != "Todos":
            df_historico = df_historico[df_historico['Animal'] == filtro_animal]
        if filtro_tipo != "Todos":
            df_historico = df_historico[df_historico['Tipo'] == filtro_tipo]
        
        # Ordenar por data (mais recente primeiro)
        df_historico = df_historico.sort_values('Data', ascending=False)
        
        st.dataframe(df_historico, use_container_width=True)
        
        # Estatísticas do histórico
        st.subheader("📊 Estatísticas de Atendimentos")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total de Atendimentos", len(df_historico))
        with col2:
            st.metric("Tipos diferentes", df_historico['Tipo'].nunique())
        with col3:
            # Extrair valores numéricos da coluna Valor
            valores = df_historico['Valor'].str.replace('R$ ', '').str.replace(',', '.').astype(float)
            st.metric("Valor Total", f"R$ {valores.sum():,.2f}")
        
        # Botão para limpar histórico
        if st.button("🗑️ Limpar Histórico"):
            st.session_state.historico = []
            st.rerun()
    else:
        st.info("Nenhum atendimento registrado ainda.")

# Rodapé
st.divider()
st.caption("© 2024 Ribeira Vet Pro - Sistema de Gestão Veterinária v23.0")
