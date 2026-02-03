import streamlit as st
import pandas as pd

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
dfBanco = pd.read_csv("dataBase/banco.csv", sep=";")
dfEstudo = pd.read_csv("dataBase/estudo.csv", sep=";", decimal=",")

dfEstudo["VALOR TOTAL"] = dfEstudo["VALOR UN."] * dfEstudo["QTD."]

ordem_colunas = [
    "PROJETO",
    "ITEM",
    "QTD.",
    "VALOR UN.",
    "VALOR TOTAL",
]

total_projeto = dfEstudo["VALOR TOTAL"].sum()

# =================================

st.title("Estudo")

tab1, tab2 = st.tabs([":material/book: Estudos", ":material/add: Adicionar"])

with tab1:
    st.metric("Total do Projeto", f"R$ {total_projeto:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    projetosMultiselect = st.multiselect(
        "",
        dfEstudo["PROJETO"].dropna().unique(),
        placeholder="Selecione o Projeto",
        key="projetos_selecionados"
    )

    for projeto in projetosMultiselect:
        st.markdown(f"### {projeto}")

        df_view = dfEstudo[dfEstudo["PROJETO"] == projeto][ordem_colunas]

        st.data_editor(df_view, width="stretch",
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
                    disabled=["", "VALOR TOTAL", "VALOR UN."],
                    )
        total_projeto = df_view["VALOR TOTAL"].sum()
        st.markdown(f"📊 **TOTAL:** R$ {total_projeto: .2f}".replace(".",","))
        st.markdown("💵 **BUGDET:** R$ 550,00")
        st.markdown(f"💰 **SAVE:** R$ {550 - total_projeto: .2f}".replace(".",","))
        st.markdown("---")