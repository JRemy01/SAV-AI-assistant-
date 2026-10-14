from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_community.retrievers import BM25Retriever
from langchain_community.document_compressors import FlashrankRerank
from langchain_classic.retrievers import EnsembleRetriever, ContextualCompressionRetriever


from pathlib import Path

from services.clean_data import load_data
EMBEDDING_MODEL = (
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)
PROJECT_DIR = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_DIR / "chroma_db"


def get_retriever():

    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    vectorstore = Chroma(
        collection_name= "sav_faq",
        embedding_function= embeddings,
        persist_directory=str(DB_PATH),
        collection_metadata={"hnsw:space":"cosine"},
    )

    vector_retriever = vectorstore.as_retriever(search_kwargs={"k":5})

    #BM25 retriever
    documents = load_data()
    bm25 = BM25Retriever.from_documents(documents)
    bm25.k = 5

    #hybrid retriever (Fuse vector & BM25)
    hybrid_retriever = EnsembleRetriever(
        retrievers = [vector_retriever, bm25],
        weights= [0.5,0.5]
    )

    # Apply reranker
    ranker = FlashrankRerank(top_n=3)

    return ContextualCompressionRetriever(
        base_compressor = ranker,
        base_retriever = hybrid_retriever
    )
