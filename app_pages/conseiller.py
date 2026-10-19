from pathlib import Path

import pandas as pd
import streamlit as st

from agent.agent import run_agent

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_DIR / "data" / "sav_requests.csv"

HIGH_PRIORITY = ["haute", "high", "urgente", "urgent"]

SUGGESTIONS = [
    "Quelles demandes urgentes sont en attente ?",
    "Où en est la demande SAV-1003 ?",
    "Combien de demandes sont en cours ?",
    "Prépare un e-mail pour SAV-1004 pour confirmer l'intervention",
]


@st.cache_data(ttl=300)
def load_requests():
    return pd.read_csv(
        DATA_PATH,
        parse_dates=["created_at", "intervention_date"],
    )


if "agent_messages" not in st.session_state:
    st.session_state.agent_messages = []

messages = st.session_state.agent_messages

st.title("Espace conseiller")
st.caption("Suivi des demandes, statistiques et préparation des réponses clients.")

df = load_requests()

tab_agent, tab_dashboard, tab_requests = st.tabs(
    ["Assistant", "Tableau de bord", "Demandes"]
)


# Agent

with tab_agent:
    header = st.container(horizontal=True, vertical_alignment="bottom")
    header.subheader("Que voulez-vous faire ?")
    if messages:
        if header.button("Nouvelle conversation", type="tertiary"):
            st.session_state.agent_messages = []
            st.rerun()

    st.caption(
        "Les e-mails sont des brouillons : relisez-les avant tout envoi."
    )

    for message in messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    question = st.chat_input(
        "Demande, numéro SAV, statistique, e-mail...",
        submit_mode="disable",
    )

    if not messages and not question:
        picked = st.pills("Exemples", SUGGESTIONS, key="agent_suggestion")
        if picked:
            question = picked

    if question:
        # History sent to the agent: previous questions and final answers only
        history = [{"role": m["role"], "content": m["content"]} for m in messages]

        messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            try:
                with st.spinner("Traitement de la demande..."):
                    answer = run_agent(question, history)
            except Exception:
                st.error(
                    "L'assistant est momentanément indisponible. "
                    "Réessayez dans quelques instants."
                )
            else:
                messages.append({"role": "assistant", "content": answer})
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
