import json
from unittest.mock import MagicMock, patch

from langchain_core.documents import Document

from agent.tools import search_faq as search_faq_module
from agent.tools.analyze_sav import analyze_sav
from agent.tools.lookup_request import lookup_request
from agent.tools.prepare_email import prepare_email
from agent.tools.search_faq import search_faq


def as_records(result):
    """Accept either a list of dicts or its JSON string."""
    return json.loads(result) if isinstance(result, str) else result



# lookup_request

def test_lookup_without_filters_returns_all_requests_without_email():
    records = as_records(lookup_request())
    assert len(records) == 12
    assert all("email" not in r for r in records)


def test_lookup_combines_filters_and_ignores_case():
    records = as_records(lookup_request(priority="haute", status="en attente"))
    assert [r["request_id"] for r in records] == ["SAV-1001"]


def test_lookup_no_match_returns_error():
    records = as_records(lookup_request(status="inconnu"))
    assert "error" in records[0]



# search_faq

def test_search_empty_query_returns_error():
    assert "error" in search_faq("   ")[0]


def test_search_returns_plain_dicts():
    doc = Document(
        page_content="## FAQ-008 — Odeur de gaz\nQuittez les lieux.",
        metadata={"faq_id": "FAQ-008", "title": "— Odeur de gaz"},
    )
    retriever = MagicMock()
    retriever.invoke.return_value = [doc]

    with patch.object(search_faq_module, "get_retriever", return_value=retriever):
        result = search_faq("odeur de gaz")

    assert result == [{
        "faq_id": "FAQ-008",
        "title": "— Odeur de gaz",
        "content": doc.page_content,
    }]
    retriever.invoke.assert_called_once_with("odeur de gaz")



# analyze_sav

def test_analyze_counts_match_data():
    stats = analyze_sav()
    assert stats["total"] == 12
    assert stats["par_statut"]["En attente"] == 4
    assert sum(stats["par_statut"].values()) == stats["total"]
    json.dumps(stats)  # must be sendable to the model



# prepare_email

def test_email_draft_uses_recipient_from_csv():
    draft = prepare_email(request_id="sav-1003", message="Un technicien passera mardi.")
    assert draft["statut"].upper() == "BROUILLON"
    assert draft["destinataire"] == "client.c@example.com"
    assert "SAV-1003" in draft["objet"]
    assert draft["corps"].startswith("Bonjour Client C")
    assert "Un technicien passera mardi." in draft["corps"]
    json.dumps(draft)


def test_email_unknown_request_returns_error():
    assert "error" in prepare_email(request_id="SAV-9999", message="test")


def test_email_empty_message_returns_error():
    assert "error" in prepare_email(request_id="SAV-1003", message="   ")


def test_email_adds_intervention_date_and_signature():
    planned = prepare_email(request_id="SAV-1004", message="Nous confirmons votre intervention.")
    not_planned = prepare_email(request_id="SAV-1003", message="Un technicien passera mardi.")

    assert "16/10/2026" in planned["corps"]
    assert "Date d'intervention" not in not_planned["corps"]
    assert planned["corps"].endswith("Le service après-vente")
