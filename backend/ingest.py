from pathlib import Path
from docling.document_converter import DocumentConverter
from docling.chunking import HybridChunker
from transformers import AutoTokenizer
from backend.config import COLLECTION_DIRS, EMBEDDING_MODEL, QDRANT_COLLECTION, COLLECTION_ACCESS
from langchain_qdrant import QdrantVectorStore, RetrievalMode
from langchain_core.documents import Document
from qdrant_client import QdrantClient
from backend.utils.embedder import dense_embeddings, sparse_embeddings


def get_all_files() -> list:
    all_files = []
    for collection, folder_path in COLLECTION_DIRS.items():
        files = Path(folder_path).glob("*")
        all_files.extend([f for f in files if f.suffix in [".pdf", ".md"]])
    return all_files

def parse_file(file: Path) -> str:
    """Reads ONE file and returns text content"""
    converter = DocumentConverter()
    dl_doc = converter.convert(file).document
    return(dl_doc)


def chunk_file(file: Path, tokenizer) -> list:
    collection = file.parent.name   # "billing", "clinical" etc.
    doc = parse_file(file)          # get document

    chunks = []

    #tokenizer = AutoTokenizer.from_pretrained(EMBEDDING_MODEL)
    chunker = HybridChunker(tokenizer=tokenizer, max_tokens=128, merge_peers=True)
    for chunk in chunker.chunk(dl_doc=doc):
        chunks.append({
            "text": chunker.serialize(chunk=chunk),     # hint: chunker.serialize(chunk=chunk)
            "source": file.name,    # hint: file.name
            "collection": collection # hint: collection variable
        })

    return chunks

def chunk_all_files() -> list:
    all_chunks = []
    tokenizer = AutoTokenizer.from_pretrained(EMBEDDING_MODEL)
    for file in get_all_files():
        chunks = chunk_file(file, tokenizer)
        all_chunks.extend(chunks)
    return all_chunks

def embedding_of_chunks():

    client = QdrantClient(url="http://localhost:6333")
    if client.collection_exists(QDRANT_COLLECTION):
        print(f"✅ Collection '{QDRANT_COLLECTION}' already exists — skipping ingestion")
        return

    else:
        all_chunks = chunk_all_files()

        docs = [Document(
            page_content=chunk["text"],
            metadata = {"source" : chunk["source"],
                        "collection" : chunk["collection"],
                        "access_roles": COLLECTION_ACCESS[chunk["collection"]]
                        }
            ) for chunk in all_chunks
                ]

        vectorstore = QdrantVectorStore.from_documents(
            documents=docs,
            embedding=dense_embeddings,
            sparse_embedding=sparse_embeddings,
            url = "http://localhost:6333",
            collection_name=QDRANT_COLLECTION,
            retrieval_mode=RetrievalMode.HYBRID,
        )

         
if __name__ == "__main__":
    embedding_of_chunks()
    print("Done! Check Qdrant dashboard at http://localhost:6333/dashboard")