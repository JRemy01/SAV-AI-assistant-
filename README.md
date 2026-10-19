# SAV Smart Assistant

An after-sales service (SAV) assistant for boiler (chaudière) support, with two interfaces:

- **Customer assistance** — a RAG chatbot that answers customer questions from an FAQ knowledge base.
- **Advisor workspace** — a tool-using agent for SAV staff: it looks up requests, computes statistics, searches the FAQ and prepares email drafts. The page also includes a dashboard and the request list.

> **Status:** working prototype. The advisor workspace is not protected yet: anyone with access to the app can open it. Add authentication (e.g. `st.login()`) before any real use.

> **Note:** the FAQ (`data/faq_chaudiere.md`) and the requests (`data/sav_requests.csv`) are fictional demo data. Replace the FAQ with the manufacturer's official documentation before any real use.

## Stack

- **UI:** Streamlit (multipage app, native charts)
- **LLM:** Groq (the model must support tool use for the agent)
- **RAG:** LangChain, Chroma (local vector store)
- **Retrieval:** hybrid search (vector + BM25), then reranking with a multilingual cross-encoder
- **Models:** `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (embeddings), `cross-encoder/mmarco-mMiniLMv2-L12-H384-v1` (reranker) — both handle French
- **Data:** pandas

## Project structure

```
sav-smart-assistant/
├── app.py                    # Entry point: navigation between the two pages
├── app_pages/
│   ├── client.py             # Customer assistance (FAQ chatbot)
│   └── conseiller.py         # Advisor workspace (agent, dashboard, requests)
├── services/
│   ├── clean_data.py         # Parses the FAQ markdown into LangChain Documents
│   ├── store_data.py         # Embeds the FAQ and stores it in Chroma
│   ├── retrieval.py          # Hybrid retriever + reranker
│   └── chatbot.py            # RAG chatbot: retrieve, then answer with Groq
├── agent/
│   ├── agent.py              # System prompt and agent loop (run_agent)
│   └── tools/
│       ├── search_faq.py     # Search the FAQ (reuses the retriever)
│       ├── lookup_request.py # Find SAV requests by ID or filters
│       ├── analyze_sav.py    # Request statistics
│       ├── prepare_email.py  # Email draft for a request (never sent)
│       ├── schemas.py        # Tool descriptions sent to the model
│       └── execute_tool.py   # Runs the tool requested by the model
├── data/
│   ├── faq_chaudiere.md      # FAQ knowledge base, one "## FAQ-XXX" section per entry
│   └── sav_requests.csv      # Sample SAV requests
├── tests/
├── .streamlit/config.toml    # Theme
├── pytest.ini
├── requirements.txt
├── .env                      # API keys (not committed)
└── chroma_db/                # Generated vector database (not committed)
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

> If you also use Anaconda, run `conda deactivate` first, or call the venv's commands directly (`.venv/bin/...`) as below. Otherwise `streamlit` may run from Anaconda and fail with `ModuleNotFoundError`.

## Usage

Run every command from the project root.

### 1. Build the vector database

```bash
.venv/bin/python -m services.store_data
```

This loads `data/faq_chaudiere.md`, splits it into one document per `## FAQ-XXX` section, embeds each one and writes them to the `sav_faq` collection in `chroma_db/` (cosine similarity). Documents use their FAQ ID as their ID, so re-running the script updates existing entries instead of duplicating them.

The first run downloads the models from Hugging Face.

### 2. Run the app

```bash
.venv/bin/streamlit run app.py
```

Two pages are available from the top navigation:

| Page | For | Content |
|------|-----|---------|
| Assistance client | Customers | FAQ chatbot with sources, gas safety notice |
| Espace conseiller | SAV staff | Agent, dashboard, filterable request list |

### 3. Use the agent from the terminal

```bash
.venv/bin/python -c "from agent.agent import run_agent; print(run_agent('Combien de demandes sont en attente ?'))"
```

`run_agent(question, history=None, step=7)` takes the previous exchanges as `history` (a list of `{"role", "content"}` messages, of which only the last `MAX_HISTORY` are sent). It does not store anything: the caller keeps the history (the app uses `st.session_state`).

### 4. Run the tests

```bash
.venv/bin/pytest                               # fast tests (no API calls, no models)
.venv/bin/pytest -m slow                       # retrieval quality (loads the models)
.venv/bin/pytest -m ""                         # everything
.venv/bin/pytest tests/test_agent_tools.py     # agent tools only
```

Slow tests are skipped by default (see `pytest.ini`). The agent loop is tested with a fake Groq client, so the test suite never calls the API.

To try the chatbot against the real API with a few sample questions:

```bash
.venv/bin/python -m tests.test_chatbot
```

## How the agent works

1. The model receives the system prompt, the recent history, the question and the tool descriptions (`schemas.py`).
2. If it asks for a tool, `execute_tool` runs it (only the tools listed in `ALLOWS_TOOLS` can run) and the result is sent back to the model.
3. This repeats until the model answers with text, or until `step` turns have been used.

Safety rules are enforced in code, not only in the prompt:

- **No email can be sent:** `prepare_email` only returns a draft, to be reviewed by an advisor.
- **The recipient, subject, intervention date and signature come from the CSV**, never from the model.
- **`lookup_request` never returns customer emails.**
- **Tool errors are returned to the model as messages** (unknown tool, malformed arguments, missing parameter), so it can correct itself. Technical details are printed in the terminal, not sent to the model.

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
| `priority`          | `Haute`, `Normale`, `Basse`                   |
| `status`            | `En attente`, `En cours`, `Intervention planifiée`, `Terminée` |
| `created_at`        | Creation date (YYYY-MM-DD)                    |
| `intervention_date` | Scheduled intervention date, if any           |
