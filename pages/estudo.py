import streamlit as st
import pandas as pd
from functions import adicionarItem, orcamento, banco, gerar_pdf

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

# ===== Carregando os dados =====
dfBanco = pd.read_csv("dataBase/banco.csv", sep=";", decimal=",")
dfEstudo = pd.read_csv("dataBase/estudo.csv", sep=";", decimal=",")
dfBudget = pd.read_csv("dataBase/budget.csv", sep=";", decimal=",")
listaProjetos = dfEstudo["PROJETO"].dropna().sort_values().unique()
listaItem = dfBanco["ITEM"].dropna().unique()

dfEstudo["VALOR TOTAL"] = dfEstudo["VALOR UN."] * dfEstudo["QTD."]

ordem_colunas = [
    "PROJETO",
    "LOCALIZAÇÃO",
    "ITEM",
    "QTD.",
    "VALOR UN.",
    "VALOR TOTAL"
]

total_projeto = dfEstudo["VALOR TOTAL"].sum()
df_budget = dfBudget[["PROJETO", "BUDGET"]]

# =================================

st.title("Estudo")


tab1, tab2 = st.tabs([":material/book: Estudos", ":material/add: Adicionar"])

with tab1:
    st.metric("Total do Projeto", f"R$ {total_projeto:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    with st.container(horizontal=True):
        if st.button(":material/add: Adicionar Item", type="primary"):
            adicionarItem(listaProjetos, listaItem, dfBanco, dfEstudo)

        with st.popover(":material/box: Total por Item"):
            total_por_item = dfEstudo.groupby("ITEM")["QTD."].sum().sort_values(ascending=False)
            st.table(total_por_item)
        
        # Aqui abaixo começa a lista suspensa para filtrar o df Estudos

    projetosMultiselect = st.multiselect(
        "",
        listaProjetos,
        placeholder="Selecione o Projeto",
        key="projetos_selecionados"
    )

    edits = {}

    for projeto in projetosMultiselect:
        st.markdown(f"### {projeto}")

        df_view = dfEstudo[dfEstudo["PROJETO"] == projeto][ordem_colunas]
        df_view_budget = df_budget[df_budget["PROJETO"] == projeto].to_dict(orient="list")
        budget_valor = df_view_budget["BUDGET"][0]
        budget_valor = float(budget_valor)
        
        

        edits[projeto] = st.data_editor(
            df_view,
            num_rows="delete",
            key=f"editor_{projeto}",
            disabled=["", "VALOR TOTAL", "VALOR UN."],
                                column_config={
                        "VALOR UN.": st.column_config.NumberColumn(
                            "VALOR UN.",
                            format="R$ %.2f",
                        ),
                        "VALOR TOTAL": st.column_config.NumberColumn(
                            "VALOR TOTAL",
                            format="R$ %.2f",
                        ),
                    },
        )

        total_projeto = df_view["VALOR TOTAL"].sum()
        st.markdown(f"📊 **TOTAL:** R$ {total_projeto: .2f}".replace(".",","))
        st.markdown(f"💵 **BUGDET:** R$ {budget_valor: .2f}".replace(".",","))
        if budget_valor - total_projeto < 0:
            st.markdown(f"❌ **OVER:** :red[R$ {budget_valor - total_projeto: .2f}]".replace(".",","))
        else:
            st.markdown(f"💰 **SAVE:** :green[R$ {budget_valor - total_projeto: .2f}]".replace(".",","))
        st.markdown("---")


    if len(projetosMultiselect) is not 0:
        if st.button(":material/save: Salvar Alterações", type="primary"):

            df_final = dfEstudo.copy()

            for projeto, df_editado in edits.items():

                # Remove todas as linhas antigas do projeto
                df_final = df_final[df_final["PROJETO"] != projeto]

                # Adiciona as novas (já com deletes aplicados)
                df_final = pd.concat([df_final, df_editado], ignore_index=True)

            df_final.to_csv(
                "dataBase/estudo.csv",
                sep=";",
                decimal=",",
                index=False
            )

            st.toast("Alterações salvas!", icon=":material/check:")
            st.rerun()

with tab2:
    with st.container(horizontal=True):
        if st.button(":material/payments: Orçamento"):
            orcamento(df_budget, dfBudget)
        if st.button(":material/database: Banco"):
            banco(dfBanco)
        if st.button("Gerar PDF"):

            pdf_bytes = gerar_pdf(total_projeto, listaProjetos, dfEstudo, df_budget)

            st.download_button(
            label="Baixar PDF",
            data=pdf_bytes,
            file_name="relatorio.pdf",
            mime="application/pdf"
        )
            st.pdf(pdf_bytes)
