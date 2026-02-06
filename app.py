import streamlit as st

st.set_page_config(layout="wide")

logo = "assets/logo.png"
with st.sidebar:
    st.logo(logo, icon_image=logo)

    pages = {
        "NAVEGAÇÃO": [
            st.Page("pages/estudo.py", title="Estudo", icon=":material/book:"),
            #st.Page("pages/projetos.py", title="Projetos", icon=":material/folder:"),
        ]
    }

pg = st.navigation(pages)
pg.run()