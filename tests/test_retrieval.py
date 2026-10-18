import pytest

from services.retrieval import get_retriever

pytestmark = pytest.mark.slow


@pytest.fixture(scope="module")
def retriever():
    return get_retriever()


@pytest.mark.parametrize(
    "question, expected",
    [
        ("Tous les combien faut-il faire l'entretien ?", "FAQ-001"),
        ("La pression de ma chaudière est trop basse", "FAQ-002"),
        ("Ma chaudière affiche une erreur F28", "FAQ-003"),
        ("Mes radiateurs restent froids, plus de chauffage", "FAQ-004"),
        ("Pas d'eau chaude au robinet", "FAQ-005"),
        ("Où en est ma demande d'intervention ?", "FAQ-006"),
        ("Ça sent le gaz dans la cuisine", "FAQ-008"),
        ("Je voudrais un devis", "FAQ-009"),
    ],
)
def test_expected_faq_in_results(retriever, question, expected):
    results = retriever.invoke(question)
    assert expected in [d.metadata["faq_id"] for d in results]


def test_returns_at_most_top_n(retriever):
    assert len(retriever.invoke("chaudière")) <= 3


def test_metadata_preserved_after_rerank(retriever):
    for doc in retriever.invoke("code erreur"):
        assert "faq_id" in doc.metadata


@pytest.mark.parametrize("question", ["?", "recette de crêpes", "presion chodière"])
def test_odd_questions_do_not_crash(retriever, question):
    assert isinstance(retriever.invoke(question), list)
