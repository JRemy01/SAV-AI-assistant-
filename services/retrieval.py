from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_community.retrievers import BM25Retriever
from langchain_community.cross_encoders import HuggingFaceCrossEncoder
from langchain_classic.retrievers.document_compressors import CrossEncoderReranker
from langchain_classic.retrievers import EnsembleRetriever, ContextualCompressionRetriever

from functools import lru_cache

from pathlib import Path

from services.clean_data import load_data
EMBEDDING_MODEL = (
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)
PROJECT_DIR = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_DIR / "chroma_db"
RANK_MODEL = "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1"

@lru_cache(maxsize=1)
def get_retriever():

    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    vectorstore = Chroma(
        collection_name= "sav_faq",
        embedding_function= embeddings,
        persist_directory=str(DB_PATH),
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
    cross_encoder = HuggingFaceCrossEncoder(model_name=RANK_MODEL)
    ranker = CrossEncoderReranker(model=cross_encoder,top_n=3)


    return ContextualCompressionRetriever(
        base_compressor = ranker,
        base_retriever = hybrid_retriever
    )
