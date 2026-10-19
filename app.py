import streamlit as st
import pandas as pd
from pathlib import Path

from services.chatbot import answer_question

PROJECT_DIR = Path(__file__).resolve().parent
DATA_PATH = PROJECT_DIR / "data" / "sav_requests.csv"

HIGH_PRIORITY = ["haute", "high", "urgente", "urgent"]

SUGGESTIONS = [
    "La pression de ma chaudière est anormale",
    "Je n'ai plus d'eau chaude",
    "Ma chaudière affiche un code erreur",
    "Où en est ma demande d'intervention ?",
]

st.set_page_config(
    page_title="SAV Chaudières",
    layout="wide",
)


@st.cache_data
def load_requests():
    return pd.read_csv(
        DATA_PATH,
        parse_dates=["created_at", "intervention_date"],
    )


def ask(question):
    """Call the chatbot and always return (answer, sources)."""
    result = answer_question(question)
    if isinstance(result, dict):
        return result.get("answer", ""), result.get("sources", [])
    return str(result), []


if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("Service après-vente chaudières")
st.caption("Dépannage, suivi des demandes et vue d'ensemble de l'activité.")

df = load_requests()

tab_chat, tab_dashboard, tab_requests = st.tabs(
    ["Dépannage", "Tableau de bord", "Demandes"]
)


# Chat interface

with tab_chat:
    header = st.container(horizontal=True, vertical_alignment="bottom")
    header.subheader("Une question sur votre chaudière ?")
    if st.session_state.messages:
        if header.button("Nouvelle conversation", type="tertiary"):
            st.session_state.messages = []
            st.rerun()

    st.warning(
        "**Odeur de gaz ?** N'actionnez aucun interrupteur, quittez les lieux "
        "et appelez Urgence Sécurité Gaz au 0 800 47 33 33."
    )

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("sources"):
                st.caption("Sources : " + ", ".join(message["sources"]))

    question = st.chat_input(
        "Décrivez votre problème",
        submit_mode="disable",
    )

    if not st.session_state.messages and not question:
        picked = st.pills(
            "Questions fréquentes",
            SUGGESTIONS,
            key="suggestion",
        )
        if picked:
            question = picked

    if question:
        st.session_state.messages.append(
            {"role": "user", "content": question}
        )
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
                st.markdown(answer)
                if sources:
                    st.caption("Sources : " + ", ".join(sources))
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "sources": sources,
                })
                st.rerun()


# SAV dashboard

with tab_dashboard:
    pending = int(df["status"].eq("En attente").sum())
    in_progress = int(df["status"].eq("En cours").sum())
    high = int(df["priority"].str.lower().isin(HIGH_PRIORITY).sum())

    with st.container(horizontal=True):
        st.metric("Demandes", len(df), border=True)
        st.metric("En attente", pending, border=True)
        st.metric("En cours", in_progress, border=True)
        st.metric("Priorité haute", high, border=True)

    status_counts = (
        df["status"].value_counts().rename_axis("Statut")
        .reset_index(name="Nombre")
    )
    issue_counts = (
        df["issue_type"].value_counts().rename_axis("Problème")
        .reset_index(name="Nombre")
    )

    col_status, col_issue = st.columns(2)
    with col_status.container(border=True):
        st.markdown("**Par statut**")
        st.bar_chart(
            status_counts, x="Statut", y="Nombre",
            horizontal=True, sort="-Nombre",
            x_label="", y_label="",
            alt="Nombre de demandes par statut",
        )
    with col_issue.container(border=True):
        st.markdown("**Par type de problème**")
        st.bar_chart(
            issue_counts, x="Problème", y="Nombre",
            horizontal=True, sort="-Nombre",
            x_label="", y_label="",
            alt="Nombre de demandes par type de problème",
        )


# Request table

with tab_requests:
    filters = st.container(horizontal=True)
    priorities = sorted(df["priority"].dropna().astype(str).unique())
    statuses = sorted(df["status"].dropna().astype(str).unique())

    with filters:
        selected_priorities = st.pills(
            "Priorité", priorities, selection_mode="multi"
        )
        selected_statuses = st.pills(
            "Statut", statuses, selection_mode="multi"
        )

    df_view = df
    if selected_priorities:
        df_view = df_view[df_view["priority"].isin(selected_priorities)]
    if selected_statuses:
        df_view = df_view[df_view["status"].isin(selected_statuses)]

    st.caption(f"{len(df_view)} demande(s) sur {len(df)}")

    st.dataframe(
        df_view,
        hide_index=True,
        alt="Liste des demandes SAV",
        column_config={
            "request_id": st.column_config.TextColumn("N° demande"),
            "customer_name": st.column_config.TextColumn("Client"),
            "email": st.column_config.TextColumn("E-mail"),
            "issue_type": st.column_config.TextColumn("Problème"),
            "priority": st.column_config.TextColumn("Priorité"),
            "status": st.column_config.TextColumn("Statut"),
            "created_at": st.column_config.DateColumn(
                "Créée le", format="DD/MM/YYYY"
            ),
            "intervention_date": st.column_config.DateColumn(
                "Intervention", format="DD/MM/YYYY"
            ),
        },
    )
