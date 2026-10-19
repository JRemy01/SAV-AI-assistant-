from pathlib import Path

from services.retrieval import get_retriever


def search_faq(query):
    query = query.strip()

    if not query:
        return [{"error": "La recherche est vide."}]

    result = get_retriever().invoke(query)

    return [
        {
            "faq_id": doc.metadata.get("faq_id"),
            "title": doc.metadata.get("title"),
            "content": doc.page_content,
        }
        for doc in result
    ]