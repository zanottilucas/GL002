import streamlit as st

st.set_page_config(layout="wide")

with st.sidebar:
    # st.logo(largeLogo, icon_image=smallLogo)

    pages = {
        "NAVEGAÇÃO": [
            st.Page("pages/estudo.py", title="Estudo", icon=":material/book:"),
            st.Page("pages/projetos.py", title="Projetos", icon=":material/folder:"),
        ]
    }

pg = st.navigation(pages)
pg.run()