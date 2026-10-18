import pandas as pd
from pathlib import Path



PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
REQUEST_PATH = PROJECT_ROOT / "data" / "sav_requests.csv"

def lookup_request(request_id=None,customer_name=None,status=None,issue_type=None,priority=None,intervention_date=None):
    df = pd.read_csv(REQUEST_PATH)

    filters = {
        "request_id":request_id,
        "customer_name":customer_name,
        "status":status,
        "issue_type":issue_type,
        "priority":priority,
        "intervention_date":intervention_date
        }

    for column,value in filters.items():
        if value is None:
            continue
        df = df[df[column].str.lower() == str(value).strip().lower()]

    if df.empty:
        return [{"error": "Aucune damande trouvée avec ces critères."}]

    df = df.drop(columns=["email"])
    result = df.fillna("").to_dict(orient = "records")
    return result