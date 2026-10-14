from pathlib import Path
import re
from langchain_core.documents import Document


data_path = Path("data/faq_chaudiere.md")
def load_data():
    data = data_path.read_text(encoding="utf-8")

    sections = re.split(
        r"(?=^## FAQ-)",
        data,
        flags=re.MULTILINE ,)

    documents = []

    for section in sections:
        section = section.strip()

        if not section.startswith("## FAQ-"):
            continue

        first_line = section.splitlines()[0]
        match = re.match(r"## (FAQ-\d+)\s*(.*)", first_line)

        if not match:
            continue

        faq_id,title = match.groups()
        doc = Document(
                        page_content= section,
                        metadata={
                            "faq_id":faq_id,
                            "title": title,
                            "source": "data/faq_chaudiere.md",
                        },
                    )
        doc.id = faq_id
        documents.append(doc)

        if not documents:
            raise ValueError("No FAQ documents available.")
    return documents