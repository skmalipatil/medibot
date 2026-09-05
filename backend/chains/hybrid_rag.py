# backend/chains/hybrid_rag.py

# ── Imports ───────────────────────────────────────────────────────────────────
from langchain_groq import ChatGroq
from qdrant_client.models import Filter, FieldCondition, MatchAny
from langchain_qdrant import QdrantVectorStore, RetrievalMode
from langchain_core.prompts import ChatPromptTemplate
from qdrant_client import QdrantClient
from backend.config import (GROQ_API_KEY, GROQ_MODEL,
                            QDRANT_COLLECTION, ROLE_ACCESS,
                            HYBRID_TOP_K, RERANK_TOP_K)
from backend.utils.embedder import dense_embeddings, sparse_embeddings, rerank_model


# ── Step 2: Build RBAC filter ─────────────────────────────────────────────────
def get_rbac_filter(role: str):
    allowed_collections = ROLE_ACCESS[role]
    rbac_filter = Filter(
        must = [FieldCondition(
            key 	= "metadata.collection",
            match 	= MatchAny(any = allowed_collections) 
        )
        ]
    )

    return(rbac_filter)


# ── Step 3: Retrieve top K docs with RBAC ─────────────────────────────────────
def retrieve(question: str, role: str) -> list:

    #defining the vector store
    vectorstore = QdrantVectorStore(
        client=QdrantClient(url="http://localhost:6333"),
        embedding=dense_embeddings,
        sparse_embedding=sparse_embeddings,
        collection_name=QDRANT_COLLECTION,
        retrieval_mode=RetrievalMode.HYBRID,
    )
    
    rbac_filter = get_rbac_filter(role)
    
    hybrid_retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": HYBRID_TOP_K, "filter": rbac_filter}
        )
        
    docs = hybrid_retriever.invoke(question)
    
    return(docs)



# ── Step 4: Rerank docs ───────────────────────────────────────────────────────
def rerank(question: str, docs: list) -> list:
    scores = rerank_model.predict(
        [(question, doc.page_content) for doc in docs]
    )
    
    scored_docs = sorted(
        zip(scores, docs),
        key=lambda x: x[0],
        reverse=True
    )
    
    return [doc for score, doc in scored_docs[:RERANK_TOP_K]]
    


# ── Step 5: Build prompt + LLM ────────────────────────────────────────────────
def build_chain():
    llm = ChatGroq(
        model=GROQ_MODEL,
        temperature=0,
        max_tokens=1024,
        reasoning_format="parsed",
        timeout=None,
        max_retries=2,
    )

    system_prompt = """You are MediBot, a helpful medical assistant.
        Answer using ONLY the context provided below.
        If the answer is not in the context, say "I don't have that information."
        Always be accurate — this is a medical system.

        Context:
        {context}"""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
    ])

    return llm, prompt


# ── Step 6: Main RAG function ─────────────────────────────────────────────────
def ask_medibot(question: str, role: str) -> dict:
    #get_rbac_filter(role)
    docs = retrieve(question, role)
    top_docs = rerank(question, docs)
    context = "\n\n".join([doc.page_content for doc in top_docs])
    # calling llm
    llm, prompt = build_chain()
    
    chain = prompt | llm
    
    response = chain.invoke({"context": context, "input": question})
    
    return{
        "answer": response.content,
        "sources": [doc.metadata.get("source") for doc in top_docs],
        "role": role,
        "retrieval_type": "hybrid_rag"
    }



# ── Test ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    result = ask_medibot(
        question="What is the ICU procedure for infection control?",
        role="nurse"
    )
    print(f"Answer: {result['answer']}")
    print(f"Sources: {result['sources']}")
    
    # debug — see which chunks reranker picked
    docs = retrieve("What is the ICU procedure for infection control?", "nurse")
    top_docs = rerank("What is the ICU procedure for infection control?", docs)
    
    print("\n=== TOP CHUNKS AFTER RERANKING ===")
    for i, doc in enumerate(top_docs):
        print(f"\nReranked Chunk {i+1}:")
        print(f"  Source: {doc.metadata.get('source')}")
        print(f"  Content: {doc.page_content[:300]}")