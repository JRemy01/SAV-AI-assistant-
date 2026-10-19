import streamlit as st

from services.chatbot import answer_question

SUGGESTIONS = [
    "La pression de ma chaudière est anormale",
    "Je n'ai plus d'eau chaude",
    "Ma chaudière affiche un code erreur",
    "Où en est ma demande d'intervention ?",
]


def ask(question):
    """Call the chatbot and always return (answer, sources)."""
    result = answer_question(question)
    if isinstance(result, dict):
        return result.get("answer", ""), result.get("sources", [])
    return str(result), []


if "client_messages" not in st.session_state:
    st.session_state.client_messages = []

messages = st.session_state.client_messages

header = st.container(horizontal=True, vertical_alignment="bottom")
header.title("Une question sur votre chaudière ?")
if messages:
    if header.button("Nouvelle conversation", type="tertiary"):
        st.session_state.client_messages = []
        st.rerun()

st.caption("Réponses issues de la documentation du service après-vente.")

st.warning(
    "**Odeur de gaz ?** N'actionnez aucun interrupteur, quittez les lieux "
    "et appelez Urgence Sécurité Gaz au 0 800 47 33 33."
)

for message in messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("sources"):
            st.caption("Sources : " + ", ".join(message["sources"]))

question = st.chat_input("Décrivez votre problème", submit_mode="disable")

if not messages and not question:
    picked = st.pills("Questions fréquentes", SUGGESTIONS, key="client_suggestion")
    if picked:
        question = picked

if question:
    messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        try:
            with st.spinner("Recherche dans la documentation..."):
                answer, sources = ask(question)
        except Exception:
            st.error(
                "Le service est momentanément indisponible. "
                "Réessayez dans quelques instants."
            )
        else:
            messages.append({
                "role": "assistant",
                "content": answer,
                "sources": sources,
            })
            st.rerun()
