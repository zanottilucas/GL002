import streamlit as st
import pandas as pd

@st.dialog(":material/payments: Orçamento")
def orcamento(df_budget, dfBudget):
    for x, y in df_budget.values:
        st.number_input(
            label=f"Orçamento para o projeto {x}",
            key=f"budget_{x}",
            value=float(y),
            min_value=0.00,
        )

    if st.button("💾 Salvar orçamentos"):
        # Atualiza o dataframe com os valores do session_state
        for idx, row in df_budget.iterrows():
            projeto = row["PROJETO"]
            df_budget.loc[idx, "BUDGET"] = st.session_state.get(
                f"budget_{projeto}", row["BUDGET"]
            )

        # Atualiza o dataframe original
        dfBudget.update(df_budget)

        # Salva no CSV
        dfBudget.to_csv("dataBase/budget.csv", sep=";", index=False)

        st.success("Orçamentos salvos com sucesso!")

@st.dialog(":material/database: Banco", width="large")
def banco(dfBanco):
    dfEditado = st.data_editor(dfBanco, width="stretch", num_rows="dynamic")
    if st.button("💾 Salvar dados"):
        # dfBanco.update(dfEditado)
        dfEditado.to_csv("dataBase/banco.csv", sep=";", decimal=",", index=False)
        st.success("Orçamentos salvos com sucesso!")
