import pandas as pd
from pathlib import Path



PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
REQUEST_PATH = PROJECT_ROOT / "data" / "sav_requests.csv"


def analyze_sav():
    df = pd.read_csv(REQUEST_PATH)

    return {
        "total": len(df),
        "par_statut": df["status"].value_counts().to_dict(),
        "par_priorite": df["priority"].value_counts().to_dict(),
        "par_probleme": df["issue_type"].value_counts().to_dict(),
    }
    