# --- 2. TUTORES (CÓDIGO CORRIGIDO E UNIFICADO) ---
elif menu == "👥 Tutores":
    st.header("Gestão de Clientes")

    # SEÇÃO PARA ADICIONAR UM NOVO TUTOR
    with st.expander("➕ Cadastrar Novo Cliente", expanded=False):
        with st.form("novo_tutor_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            nome = col1.text_input("Nome Completo").upper()
            cpf = col2.text_input("CPF")
            zap = col1.text_input("WhatsApp")
            end = col2.text_input("Endereço Completo")
            if st.form_submit_button("✅ SALVAR NOVO CLIENTE"):
                if nome and zap:
                    c.execute("INSERT INTO tutores (nome, zap, endereco, cpf) VALUES (?,?,?,?)", (nome, zap, end, cpf))
                    conn.commit()
                    st.success("Cliente cadastrado com sucesso!")
                    st.rerun()

    st.divider()
    st.header("✏️ Editar ou Apagar Cliente")

    # --- INÍCIO DA NOVA SEÇÃO DE EDIÇÃO ---

    # 1. BUSCAR E SELECIONAR O TUTOR PARA EDITAR
    tutores_para_editar = c.execute("SELECT id, nome FROM tutores ORDER BY nome").fetchall()
    
    if not tutores_para_editar:
        st.info("Nenhum cliente cadastrado para editar.")
    else:
        # Cria uma lista de nomes para o seletor, incluindo uma opção para não selecionar ninguém
        opcoes_tutores = ["Selecione um cliente para editar..."] + [t[1] for t in tutores_para_editar]
        tutor_nome_selecionado = st.selectbox("Escolha um cliente", opcoes_tutores)

        # 2. SE UM TUTOR FOI SELECIONADO, MOSTRAR O FORMULÁRIO DE EDIÇÃO
        if tutor_nome_selecionado != "Selecione um cliente para editar...":
            # Busca todos os dados do tutor selecionado no banco de dados
            tutor_id_selecionado = [t[0] for t in tutores_para_editar if t[1] == tutor_nome_selecionado][0]
            tutor_atual = c.execute("SELECT nome, cpf, zap, endereco FROM tutores WHERE id = ?", (tutor_id_selecionado,)).fetchone()
            
            with st.form("edit_tutor_form"):
                st.subheader(f"Editando: {tutor_atual[0]}")
                
                # Campos do formulário pré-preenchidos com os dados atuais
                edit_nome = st.text_input("Nome Completo", value=tutor_atual[0]).upper()
                edit_cpf = st.text_input("CPF", value=tutor_atual[1])
                edit_zap = st.text_input("WhatsApp", value=tutor_atual[2])
                edit_end = st.text_input("Endereço Completo", value=tutor_atual[3])

                col_salvar, col_apagar = st.columns(2)

                # 3. BOTÃO DE SALVAR ALTERAÇÕES
                if col_salvar.form_submit_button("💾 SALVAR ALTERAÇÕES"):
                    c.execute("""UPDATE tutores SET nome=?, cpf=?, zap=?, endereco=? WHERE id=?""",
                              (edit_nome, edit_cpf, edit_zap, edit_end, tutor_id_selecionado))
                    conn.commit()
                    st.success(f"Dados de {edit_nome} atualizados com sucesso!")
                    st.rerun()

                # 4. BOTÃO DE APAGAR (COM CONFIRMAÇÃO)
                if col_apagar.form_submit_button("❌ APAGAR CLIENTE"):
                    c.execute("DELETE FROM tutores WHERE id=?", (tutor_id_selecionado,))
                    conn.commit()
                    st.warning(f"Cliente {tutor_atual[0]} foi apagado permanentemente!")
                    st.rerun()

    # --- FIM DA SEÇÃO DE EDIÇÃO ---

    st.divider()
    st.subheader("📋 Lista Completa de Clientes")
    busca = st.text_input("🔍 Pesquisar Cliente")
    lista_completa = c.execute("SELECT nome, zap, endereco FROM tutores WHERE nome LIKE ?", (f"%{busca}%",)).fetchall()
    st.dataframe(pd.DataFrame(lista_completa, columns=["Nome", "WhatsApp", "Endereço"]), use_container_width=True)
