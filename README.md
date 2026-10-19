# SAV Smart Assistant

A smart after-sales service (SAV) assistant for boiler (chaudière) support. It answers customer questions from an FAQ knowledge base using retrieval-augmented generation (RAG), and works with a dataset of SAV requests.

> **Status:** work in progress. The FAQ ingestion and vector indexing are implemented; the chatbot (`services/chatbot.py`) and the Streamlit app (`app.py`) are not written yet.

> **Note:** the FAQ content in `data/faq_chaudiere.md` is fictional demo data. Replace it with the manufacturer's official documentation before any real use.

## Stack

- **UI:** Streamlit, Plotly
- **LLM:** Groq
- **RAG:** LangChain, Chroma (local vector store)
- **Embeddings:** `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (multilingual, handles French content)
- **Data:** pandas

## Project structure

```
sav-smart-assistant/
├── app.py                  # Streamlit app (to be implemented)
├── requirements.txt
├── .env                    # API keys (not committed)
├── data/
│   ├── faq_chaudiere.md    # FAQ knowledge base, one "## FAQ-XXX" section per entry
│   └── sav_requests.csv    # Sample SAV requests
├── services/
│   ├── clean_data.py       # Parses the FAQ markdown into LangChain Documents
│   ├── store_data.py       # Embeds the FAQ and stores it in Chroma
│   └── chatbot.py          # RAG chatbot (to be implemented)
└── chroma_db/              # Generated vector database (not committed)
```

## Setup

Requires Python 3.10+.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file at the project root:

```env
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=your_groq_model_name
```

## Usage

### 1. Build the vector database

```bash
python services/store_data.py
```

This loads `data/faq_chaudiere.md`, splits it into one document per `## FAQ-XXX` section, embeds each one and writes them to the `sav_faq` collection in `chroma_db/` (cosine similarity). Documents use their FAQ ID as their ID, so re-running the script updates existing entries instead of duplicating them.

The first run downloads the embedding model from Hugging Face.

### 2. Run the app

```bash
streamlit run app.py
```

(Available once `app.py` is implemented.)

### 3. Run the tests

```bash
.venv/bin/pytest                               # fast tests (FAQ parsing, agent tools)
.venv/bin/pytest -m slow                       # retrieval quality (loads the models)
.venv/bin/pytest -m ""                         # everything
.venv/bin/pytest tests/test_agent_tools.py     # agent tools only
```

Slow tests are skipped by default (see `pytest.ini`).

## Data

### FAQ (`data/faq_chaudiere.md`)

Each entry follows this format:

```markdown
## FAQ-001 — Entretien périodique
Question : ...
Réponse : ...
```

The ID (`FAQ-001`) and title are stored as document metadata, along with the source file.

### SAV requests (`data/sav_requests.csv`)

| Column              | Description                                   |
|---------------------|-----------------------------------------------|
| `request_id`        | Request ID, e.g. `SAV-1001`                   |
| `customer_name`     | Customer name                                 |
| `email`             | Customer email                                |
| `issue_type`        | Issue category (e.g. `Code erreur`, `Entretien`) |
| `priority`          | `Haute`, `Normale`, ...                       |
| `status`            | `En attente`, `En cours`, `Terminée`, ...     |
| `created_at`        | Creation date (YYYY-MM-DD)                    |
| `intervention_date` | Scheduled intervention date, if any           |
