import pytest

from services import clean_data


@pytest.fixture
def faq_file(tmp_path, monkeypatch):
    path = tmp_path / "faq.md"
    monkeypatch.setattr(clean_data, "data_path", path)
    return path


def test_loads_all_faq_documents():
    docs = clean_data.load_data()
    assert len(docs) == 10
    for doc in docs:
        assert doc.metadata["faq_id"].startswith("FAQ-")
        assert doc.id == doc.metadata["faq_id"]
        assert doc.page_content.startswith("## FAQ-")
        assert doc.metadata["source"] == "data/faq_chaudiere.md"


def test_ids_are_unique():
    ids = [doc.id for doc in clean_data.load_data()]
    assert len(ids) == len(set(ids))


def test_title_is_parsed():
    first = clean_data.load_data()[0]
    assert first.metadata["faq_id"] == "FAQ-001"
    assert "Entretien périodique" in first.metadata["title"]


def test_intro_text_is_not_a_document():
    docs = clean_data.load_data()
    assert all("Version de démonstration" not in d.page_content for d in docs)


def test_works_from_another_directory(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert len(clean_data.load_data()) > 0


def test_empty_file_raises(faq_file):
    faq_file.write_text("# Nothing here\n", encoding="utf-8")
    with pytest.raises(ValueError):
        clean_data.load_data()


def test_section_without_number_is_skipped(faq_file):
    faq_file.write_text(
        "## FAQ-001 — Valid\nQuestion : ok\n\n## FAQ- broken\nQuestion : ko\n",
        encoding="utf-8",
    )
    docs = clean_data.load_data()
    assert [d.id for d in docs] == ["FAQ-001"]


def test_accents_are_preserved(faq_file):
    faq_file.write_text("## FAQ-042 — Chaudière à gaz\nRéponse : été\n", encoding="utf-8")
    doc = clean_data.load_data()[0]
    assert "Chaudière à gaz" in doc.metadata["title"]
    assert "été" in doc.page_content
