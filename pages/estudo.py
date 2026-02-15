import streamlit as st
import pandas as pd
import os
import zipfile
import io
from datetime import datetime
from functions import adicionarItem, orcamento, banco, gerar_pdf, mudar_titulo, init_state

st.markdown(
    """
    <style>
    /* container da tabela */
    .stTable {
        width: 100%;
        overflow-x: auto;
    }

    /* tabela */
    .stTable table {
        width: max-content;
        min-width: 100%;
        border-collapse: collapse;
    }

    /* células */
    .stTable th, .stTable td {
        white-space: nowrap;
        padding: 6px 10px;
        font-size: 14px;
    }

    /* cabeçalho */
    .stTable th {
        background-color: #f5f5f5;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True
)


tab1, tab2, tab3 = st.tabs([":material/database: Banco de Dados", ":material/add: Adicionar", ":material/book: Estudos"])


with tab1:

    st.badge("Ao alterar o upload de .zip, é necessário dar F5 para limpar o cache do antigo .zip", color="yellow", icon=":material/warning:")
    uploaded_zip = st.file_uploader("Upload ZIP", type="zip")

    if uploaded_zip:

        dfBanco = None
        dfEstudo = None
        dfBudget = None
        dfTitulo = None

        with zipfile.ZipFile(uploaded_zip) as z:

            for nome in z.namelist():
                base = os.path.basename(nome)

                st.markdown(base)

                if base == "banco.csv":
                    with z.open(nome) as f:
                        dfBanco = pd.read_csv(f, sep=";", decimal=",")

                elif base == "estudo.csv":
                    with z.open(nome) as f:
                        dfEstudo = pd.read_csv(f, sep=";", decimal=",")

                elif base == "budget.csv":
                    with z.open(nome) as f:
                        dfBudget = pd.read_csv(f, sep=";", decimal=",")

                elif base == "nomeEstudo.csv":
                    with z.open(nome) as f:
                        dfTitulo = pd.read_csv(f, sep=";")

        # ✅ Só inicializa se tudo foi carregado
        if all(v is not None for v in [dfBanco, dfEstudo, dfBudget, dfTitulo]):
            init_state(dfBanco, dfEstudo, dfBudget, dfTitulo)
            st.success("Dados carregados no session_state")
        else:
            st.error("ZIP incompleto — faltam arquivos")

        with st.popover("Session State"):
            st.write(st.session_state)

    if uploaded_zip != None:

        with tab2:

            st.title(st.session_state.dfTitulo.loc[0, "NOME DO ESTUDO"])

            titulo = st.session_state.dfTitulo["NOME DO ESTUDO"].to_list()
            listaProjetos = st.session_state.dfEstudo["PROJETO"].dropna().sort_values().unique()
            listaItem = st.session_state.dfBanco["ITEM"].dropna().unique()

            dfEstudo["VALOR TOTAL"] = dfEstudo["VALOR UN."] * dfEstudo["QTD."]

            ordem_colunas = [
                "PROJETO",
                "LOCALIZAÇÃO",
                "ITEM",
                "QTD.",
                "VALOR UN.",
                "VALOR TOTAL",
                "OBS"
            ]

            total_projeto = dfEstudo["VALOR TOTAL"].sum()
            df_budget = dfBudget[["PROJETO", "BUDGET"]]

            # =================================


            st.markdown("### Ações:")

            pdf_bytes = None

            with st.container(horizontal=True, border=True):
                if st.button(":material/settings: Configuração"):
                    mudar_titulo(titulo, dfTitulo)
                if st.button(":material/payments: Orçamento"):
                    orcamento()
                if st.button(":material/database: Banco"):
                    banco()

                zip_buffer = io.BytesIO()

                with zipfile.ZipFile(zip_buffer, "w") as z:

                    z.writestr(
                        "banco.csv",
                        st.session_state.dfBanco.to_csv(sep=";", decimal=",", index=False)
                    )

                    z.writestr(
                        "estudo.csv",
                        st.session_state.dfEstudo.to_csv(sep=";", decimal=",", index=False)
                    )

                    z.writestr(
                        "budget.csv",
                        st.session_state.dfBudget.to_csv(sep=";", decimal=",", index=False)
                    )

                    z.writestr(
                        "nomeEstudo.csv",
                        st.session_state.dfTitulo.to_csv(sep=";", index=False)
                    )

                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                nome_zip = f"dados_{timestamp}.zip"

                st.download_button(
                    ":material/backup: Baixar tudo (ZIP)",
                    zip_buffer.getvalue(),
                    nome_zip,
                    "application/zip"
                )

                if st.button(":material/picture_as_pdf: Gerar PDF", type="primary"):

                    pdf_bytes = gerar_pdf()

                    st.download_button(
                    label=":material/download: Baixar PDF",
                    data=pdf_bytes,
                    file_name="relatorio.pdf",
                    mime="application/pdf",
                    type="primary"
                    )
                
                if pdf_bytes is not None:
                    st.pdf(pdf_bytes)
                


        with tab3:

            # 🔹 Sempre iniciar estado
            #init_state(dfBanco, dfEstudo, dfBudget, dfTitulo)

            st.title(st.session_state.dfTitulo.loc[0, "NOME DO ESTUDO"])

            # 🔹 Usar SOMENTE session_state daqui pra frente
            dfEstudo = st.session_state.dfEstudo
            dfBudget = st.session_state.dfBudget

            dfEstudo["VALOR TOTAL"] = dfEstudo["VALOR UN."] * dfEstudo["QTD."]

            listaProjetos = dfEstudo["PROJETO"].dropna().sort_values().unique()

            ordem_colunas = [
                "PROJETO",
                "LOCALIZAÇÃO",
                "ITEM",
                "QTD.",
                "VALOR UN.",
                "VALOR TOTAL",
                "OBS"
            ]

            total_global = dfEstudo["VALOR TOTAL"].sum()

            st.metric(
                "Total do Projeto",
                f"R$ {total_global:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            )

            # =====================================================
            # AÇÕES
            # =====================================================

            with st.container(horizontal=True):

                if st.button(":material/add: Adicionar Item", type="primary"):
                    listaItem = st.session_state.dfBanco["ITEM"].dropna().unique()
                    adicionarItem(listaProjetos, listaItem)

                with st.popover(":material/box: Total por Item"):
                    total_por_item = (
                        dfEstudo.groupby("ITEM")["QTD."]
                        .sum()
                        .sort_values(ascending=False)
                    )
                    st.table(total_por_item)

            # =====================================================
            # FILTRO PROJETOS
            # =====================================================

            projetosMultiselect = st.multiselect(
                "",
                listaProjetos,
                placeholder="Selecione o Projeto",
                key="projetos_selecionados"
            )

            edits = {}

            for projeto in projetosMultiselect:

                st.markdown(f"### {projeto}")

                df_view = dfEstudo[dfEstudo["PROJETO"] == projeto][ordem_colunas].copy()

                budget_valor = float(
                    dfBudget.loc[dfBudget["PROJETO"] == projeto, "BUDGET"].iloc[0]
                )

                edits[projeto] = st.data_editor(
                    df_view,
                    num_rows="delete",
                    key=f"editor_{projeto}",
                    disabled=["VALOR TOTAL", "VALOR UN."],
                    column_config={
                        "VALOR UN.": st.column_config.NumberColumn(
                            "VALOR UN.", format="R$ %.2f"
                        ),
                        "VALOR TOTAL": st.column_config.NumberColumn(
                            "VALOR TOTAL", format="R$ %.2f"
                        ),
                    },
                )

                total_projeto = df_view["VALOR TOTAL"].sum()

                st.markdown(f"📊 **TOTAL:** R$ {total_projeto:.2f}".replace(".", ","))
                st.markdown(f"💵 **BUDGET:** R$ {budget_valor:.2f}".replace(".", ","))

                diff = budget_valor - total_projeto

                if diff < 0:
                    st.markdown(f"❌ **OVER:** :red[R$ {diff:.2f}]".replace(".", ","))
                else:
                    st.markdown(f"💰 **SAVE:** :green[R$ {diff:.2f}]".replace(".", ","))

                st.markdown("---")

            # =====================================================
            # SALVAR ALTERAÇÕES
            # =====================================================

            if projetosMultiselect:

                if st.button(":material/save: Salvar Alterações", type="primary"):

                    df_final = dfEstudo.copy()

                    for projeto, df_editado in edits.items():

                        df_final = df_final[df_final["PROJETO"] != projeto]
                        df_final = pd.concat([df_final, df_editado], ignore_index=True)

                    # 🔹 Atualiza session_state
                    st.session_state.dfEstudo = df_final

                    st.toast("Alterações salvas!", icon=":material/check:")
                    st.rerun()

