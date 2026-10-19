import streamlit as st

st.set_page_config(
    page_title="SAV Chaudières",
    layout="wide",
)

page = st.navigation(
    [
        st.Page("app_pages/client.py", title="Assistance client", default=True),
        st.Page("app_pages/conseiller.py", title="Espace conseiller"),
    ],
    position="top",
)

page.run()
