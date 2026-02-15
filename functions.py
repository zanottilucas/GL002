import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime
from babel.dates import format_date
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    LongTable,
    PageBreak,
    Image
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.platypus import TableStyle
from reportlab.lib import colors

import matplotlib.pyplot as plt
import numpy as np

import matplotlib
import matplotlib as mpl


def init_state(dfBanco, dfEstudo, dfBudget, dfTitulo):

    if "dfBanco" not in st.session_state:
        st.session_state.dfBanco = dfBanco.copy()

    if "dfEstudo" not in st.session_state:
        st.session_state.dfEstudo = dfEstudo.copy()

    if "dfBudget" not in st.session_state:
        st.session_state.dfBudget = dfBudget.copy()

    if "dfTitulo" not in st.session_state:
        st.session_state.dfTitulo = dfTitulo.copy()




@st.dialog(":material/payments: Orçamento")
def orcamento():

    df_budget = st.session_state.dfBudget

    # ---------- Inicializa chaves ----------
    for _, row in df_budget.iterrows():
        key = f"budget_{row['PROJETO']}"
        if key not in st.session_state:
            st.session_state[key] = float(row["BUDGET"])

    # ---------- Inputs ----------
    for _, row in df_budget.iterrows():
        projeto = row["PROJETO"]

        st.number_input(
            label=f"Orçamento para o projeto {projeto}",
            key=f"budget_{projeto}",
            min_value=0.00,
        )

    # ---------- Salvar ----------
    if st.button("💾 Salvar orçamentos"):

        for idx, row in df_budget.iterrows():
            projeto = row["PROJETO"]
            df_budget.loc[idx, "BUDGET"] = st.session_state[f"budget_{projeto}"]

        st.session_state.dfBudget = df_budget

        st.success("Orçamentos salvos com sucesso!")
        st.rerun()

@st.dialog(":material/database: Banco", width="large")
def banco():

    dfEditado = st.data_editor(
        st.session_state.dfBanco,
        width="stretch",
        num_rows="dynamic",
        key="editor_banco"
    )

    if st.button("💾 Salvar dados"):

        # ⭐ Atualiza o session_state
        st.session_state.dfBanco = dfEditado.copy()

        st.success("Salvo com sucesso!")
        st.rerun()
    
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

        if not obs or obs.strip() == "":
            obs = "Sem observação"

        novo_item = {
            "LOCALIZAÇÃO": localizacao,
            "PROJETO": projeto,
            "ITEM": item,
            "FORNECEDOR": fornecedor,
            "VALOR UN.": valor_un,
            "QTD.": qtd,
            "OBS": obs
        }

        dfEstudo.loc[len(dfEstudo)] = novo_item
        dfEstudo.to_csv("dataBase/estudo.csv", sep=";", decimal=",", index=False)
        st.rerun()
        st.success("Item adicionado com sucesso!")

# -----------------------------
# CAPA (desenhada via canvas)
# -----------------------------
def primeira_pagina(canvas, doc):
    capa_relatorio = "assets/capa_relatorio.png"
    w, h = A4

    dfTitulo = pd.read_csv("dataBase/nomeEstudo.csv", sep=";")
    titulo = st.session_state.dfTitulo["NOME DO ESTUDO"].to_list()

    data = datetime.now()
    formatada = format_date(data, "d 'de' MMMM 'de' y", locale="pt_BR")

    canvas.drawImage(capa_relatorio, 0, 0, width=w, height=h)
    canvas.setFont("Helvetica", 20)
    canvas.drawString(45, 550, titulo[0])
    canvas.drawString(45, 500, formatada)


# -----------------------------
# HEADER / FOOTER opcional
# (páginas seguintes)
# -----------------------------
def outras_paginas(canvas, doc):
    canvas.setFont("Helvetica", 9)
    canvas.drawString(40, 20, f"Página {doc.page}")


# -----------------------------
# GERAR PDF
# -----------------------------
def gerar_pdf():

    dfEstudo = st.session_state.dfEstudo.copy()
    dfBudget = st.session_state.dfBudget.copy()

    dfEstudo["VALOR TOTAL"] = dfEstudo["VALOR UN."] * dfEstudo["QTD."]

    listaProjetos = (
        dfEstudo["PROJETO"]
        .dropna()
        .sort_values()
        .unique()
    )

    df_budget = dfBudget[["PROJETO", "BUDGET"]]

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    story = []

    # 👇 Garante que a capa fique sozinha
    story.append(PageBreak())

    # -------- Conteúdo automático --------
    story.append(Paragraph("Relatório de Dados", styles["Heading1"]))
    story.append(Spacer(1, 12))

    #story.append(Paragraph(f"Total do projeto: R$ {total_projeto: .2f}".replace(".",","), styles["Heading1"])) --> Tem um Bug, quando tem um multiselect na outra aba, ele soma errado.

    ordem_colunas = [
    "PROJETO",
    "LOCALIZAÇÃO",
    "ITEM",
    "QTD.",
    "VALOR UN.",
    "VALOR TOTAL"
]

 
    for projeto in listaProjetos:

        df_view = dfEstudo[dfEstudo["PROJETO"] == projeto][ordem_colunas]
        total_projeto = df_view["VALOR TOTAL"].sum()
        df_view["VALOR UN."] = df_view["VALOR UN."].map(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        df_view["VALOR TOTAL"] = df_view["VALOR TOTAL"].map(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

        df_view_budget = df_budget[df_budget["PROJETO"] == projeto].to_dict(orient="list")
        budget_valor = float(df_view_budget["BUDGET"][0])

        story.append(Paragraph(f"{projeto}", styles["Heading2"]))
        story.append(Paragraph(f"Total do Projeto: R${total_projeto: .2f}".replace(",", "X").replace(".", ",").replace("X", "."), styles["Heading4"]))
        story.append(Paragraph(f"Budget: R${budget_valor: .2f}".replace(",", "X").replace(".", ",").replace("X", "."), styles["Heading4"]))
        
        diff = budget_valor - total_projeto

        if diff < 0:
            texto = f'OVER: <font color="red">R$ {diff: .2f}</font>'.replace(",", "X").replace(".", ",").replace("X", ".")   
        else:
            texto = f'SAVE: <font color="green">R${diff: .2f}</font>'.replace(",", "X").replace(".", ",").replace("X", ".")

        story.append(Paragraph(texto, styles["Heading4"]))

        # ---- converter dataframe ----
        dados = df_view.values.tolist()

        # ---- montar tabela ----
        colunas = [ordem_colunas] + dados
        
        style = getSampleStyleSheet()["BodyText"]

        dados_formatados = [
            [Paragraph(str(c), style) for c in linha]
            for linha in dados
        ]

        colunas = [ordem_colunas] + dados_formatados


        tabela = LongTable(
            colunas,
            repeatRows=1
        )

        tabela.setStyle(TableStyle([

            # Linhas
            ("GRID", (0,0), (-1,-1), 0.25, colors.black),

            # Cabeçalho
            ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
            ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),

            # Padding
            ("LEFTPADDING", (0,0), (-1,-1), 4),
            ("RIGHTPADDING", (0,0), (-1,-1), 4),
            ("TOPPADDING", (0,0), (-1,-1), 2),
            ("BOTTOMPADDING", (0,0), (-1,-1), 2),
        ]))

        story.append(tabela)

    # Aqui vem a tabela de total por item

    story.append(Spacer(1, 12))
    story.append(Paragraph("Total por item", styles["Heading1"]))
    story.append(Spacer(1, 12))

    total_por_item = (
        dfEstudo
        .groupby("ITEM")["QTD."]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )


    dados = total_por_item.values.tolist()
    colunas = [total_por_item.columns.tolist()] + dados

    tabela = LongTable(colunas, repeatRows=1)

    tabela.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.25, colors.black),
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("ALIGN", (-1,1), (-1,-1), "RIGHT"),
    ]))

    story.append(tabela)

    # Aqui vem o gráfico de heat

    story.append(Spacer(1, 12))
    story.append(Paragraph("Distribuição de Itens por Projeto", styles["Heading1"]))
    story.append(Spacer(1, 12))

    # ---- cria matriz pivot ----
    pivot = dfEstudo.pivot_table(
        index="PROJETO",
        columns="ITEM",
        values="QTD.",
        aggfunc="sum",
        fill_value=0
    )

    projetos = pivot.index.tolist()
    itens = pivot.columns.tolist()
    matrix = pivot.values


    # ---- gera heatmap ----
    fig, ax = plt.subplots(figsize=(10, 6))

    im = ax.imshow(matrix)

    # Barra de cor com label
    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label("Quantidade (QTD.)")

    ax.set_xticks(range(len(itens)))
    ax.set_xticklabels(itens, rotation=45, ha="right")

    ax.set_yticks(range(len(projetos)))
    ax.set_yticklabels(projetos)

    # valores nas células
    for i in range(len(projetos)):
        for j in range(len(itens)):
            ax.text(j, i, int(matrix[i, j]),
                    ha="center", va="center")

    ax.set_title("Quantidade por Item e Projeto")

    fig.tight_layout()


    # ---- converte para imagem reportlab ----
    img_buffer = BytesIO()
    fig.savefig(img_buffer, format="png", dpi=200, bbox_inches="tight")
    plt.close(fig)
    img_buffer.seek(0)

    img = Image(img_buffer, width=480, height=300)

    story.append(img)

    # build do documento
    doc.build(
        story,
        onFirstPage=primeira_pagina,
        onLaterPages=outras_paginas
    )

    buffer.seek(0)

    return buffer.getvalue()

@st.dialog(":material/settings: Configuração")
def mudar_titulo(titulo, dfTitulo):
    mudarTitulo = st.text_input("Título", placeholder= titulo[0], value=st.session_state.dfTitulo.loc[0, "NOME DO ESTUDO"])

    if st.button(":material/refresh: Atualizar", type="primary"):

        st.session_state.dfTitulo.loc[0, "NOME DO ESTUDO"] = mudarTitulo
        
        st.success("Alteração feita com sucesso!")
        st.rerun()
        



