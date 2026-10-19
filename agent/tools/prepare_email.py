import pandas as pd
from pathlib import Path



PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
REQUEST_PATH = PROJECT_ROOT / "data" / "sav_requests.csv"


def prepare_email(request_id, message):
    if not message or not message.strip():
        return {"error": "Aucun message."}

    if not request_id or not request_id.strip():
        return {"error": "Numéro de demande manquant."}

    df = pd.read_csv(REQUEST_PATH)
    match = df[df["request_id"].str.lower() == request_id.strip().lower()]

    if match.empty:
        return {"error": "Demande introuvable."}

    row = match.iloc[0]

    # Facts come from the CSV, not from the model
    intervention = ""
    if pd.notna(row["intervention_date"]):
        date = pd.to_datetime(row["intervention_date"]).strftime("%d/%m/%Y")
        intervention = f"Date d'intervention prévue : {date}.\n\n"

    return {
        "statut": "Brouillon",
        "destinataire": row["email"],
        "objet": f"Votre demande {row['request_id']} : {row['issue_type']}",
        "corps":(
            f"Bonjour {row['customer_name']},\n\n"
            f"{message.strip()}\n\n"
            f"{intervention}"
            "Cordialement,\n"
            "Le service après-vente"
        ),
    }