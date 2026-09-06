from semantic_router import Route
from semantic_router.routers import SemanticRouter
from semantic_router.encoders import HuggingFaceEncoder
from backend.config import EMBEDDING_MODEL, SQL_RAG_ROLES

from fastapi import APIRouter
from pydantic import BaseModel
from backend.chains.hybrid_rag import ask_medibot
from backend.chains.sql_chain import sql_rag_chain

router = APIRouter()

encoder = HuggingFaceEncoder(name=EMBEDDING_MODEL)

sql_route = Route(
	name = "sql_route",
	utterances = [
		"How many claims were rejected?",
		"Which equipment category has most open tickets?",
		"What is the total approved amount for all claims?",
		"How many tickets are still in progress?",
		"What is total approved amount?",
		"Which department has most claims?"
		]
	)
	
	
rag_route = Route(
	name = "rag_route",
	utterances = [
		"What is the ICU procedure for infection control?",
		"What are the drugs available under Gastrointestinal & Endocrine Drugs?",
		"What are the standard trement method for Type 2 Diabetes Mellitus?",
		"what are the hr leave policy?",
		"How do I submit a claim?"
		]
	)
	
routes = [sql_route, rag_route]


sr = SemanticRouter(
    encoder=encoder,
    routes=routes,
    auto_sync="local",   # store route vectors locally in memory
)


class ChatRequest(BaseModel):
    question: str   # must be a string
    role: str       # must be a string

def route_questions(questions: str, role: str) -> str:
    if role not in SQL_RAG_ROLES:
        return "rag_route"
    else:
        result = sr(questions)
        if result.name is None:   
            return "rag_route"
        return result.name    
		
# ── Chat endpoint ─────────────────────────────────────────────
@router.post("/chat")
def chat(request: ChatRequest):
    route = route_questions(request.question, request.role)
    
    if route == "sql_route":
        answer = sql_rag_chain(request.question)
        return {
            "answer": answer,
            "sources": [],
            "retrieval_type": "sql_rag",
            "role": request.role
        }
    else:
        result = ask_medibot(request.question, request.role)
        return result