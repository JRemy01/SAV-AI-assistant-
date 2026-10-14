from pathlib import Path

from langchain_chroma import Chroma
from langchain_text_splitters import TextSplitter
from langchain_huggingface import HuggingFaceEmbeddings

from services.clean_data import load_data

EMBEDDING_MODEL = (
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)
PROJECT_DIR = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_DIR / "chroma_db"

def build_vector():
    documents = load_data()

    embeddings = HuggingFaceEmbeddings(model_name= EMBEDDING_MODEL)

    vectorstore = Chroma(
        collection_name= "sav_faq",
        embedding_function= embeddings,
        persist_directory=str(DB_PATH),
        collection_metadata={"hnsw:space":"cosine"},
    )

    # update the vector
    ids_list = [doc.id for doc in documents]
    vectorstore.add_documents(documents=documents,ids=ids_list)

    print(f"Indexed {len(documents)} FAQ documents.")
    print(f"Vector database: {DB_PATH}")

if __name__== "__main__":
    build_vector()