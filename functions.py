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
        st.success("Salvo com sucesso!")
    
@st.dialog(":material/add: Adicionar Item", width="large")
def adicionarItem(listaProjetos, listaItem, dfBanco, dfEstudo):
    listaLocalizacao = dfEstudo["LOCALIZAÇÃO"].dropna().unique()
    localizacao = st.selectbox("Localização", listaLocalizacao, accept_new_options=True)
    projeto = st.pills("Selecione o projeto:", listaProjetos, default = listaProjetos[0])
    item = st.selectbox("Item", listaItem)
    valorFornecedor = dfBanco.loc[dfBanco["ITEM"] == item, "FORNECEDOR"]
    valorUnitario = dfBanco.loc[dfBanco["ITEM"] == item, "VALOR UN."]
    fornecedor = st.text_input("Fornecedor", disabled=True, value = valorFornecedor.iloc[0] if not valorFornecedor.empty else "")
    valor_un = st.number_input("Valor Unitário", min_value=0.00, disabled = True, value = float(valorUnitario.iloc[0]) if not valorUnitario.empty else 0.0)
    qtd = st.number_input("Quantidade", min_value=0.00)
    obs = st.text_area("Observação")

    if st.button("Adicionar"):
        novo_item = {
            "LOCALIZAÇÃO": localizacao,
            "PROJETO": projeto,
            "ITEM": item,
            "FORNECEDOR": fornecedor,
            "VALOR UN.": valor_un,
            "QTD.": qtd,
            "OBS.": obs
        }
        dfEstudo.loc[len(dfEstudo)] = novo_item
        dfEstudo.to_csv("dataBase/estudo.csv", sep=";", decimal=",", index=False)
        st.rerun()
        st.success("Item adicionado com sucesso!")