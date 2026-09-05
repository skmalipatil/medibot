# backend/chains/sql_chain.py
import re
from langchain_community.utilities import SQLDatabase
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
#from langchain.chains import create_sql_query_chain
from langchain_classic.chains import create_sql_query_chain
from backend.config import DB_PATH, GROQ_API_KEY, GROQ_MODEL

# ── Connect to DB ─────────────────────────────────────────────
db = SQLDatabase.from_uri(f"sqlite:///{DB_PATH}")

# ── LLM ──────────────────────────────────────────────────────
llm = ChatGroq(
    api_key=GROQ_API_KEY,
    model=GROQ_MODEL,
    temperature=0,
)

# ── Clean SQL (from your class) ───────────────────────────────
def clean_sql(raw: str) -> str:
    raw = re.sub(r"```(?:sql)?", "", raw).strip("`").strip()
    if "SQLQuery:" in raw:
        raw = raw.split("SQLQuery:")[-1].strip()
    return raw


SYSTEM_PROMPT = """You are MediBot, a medical analytics assistant.
Given a user question and SQL result from MediAssist database,
provide a clear, concise natural language answer.
Be specific with numbers and facts from the data."""
# ── SQL RAG Chain ─────────────────────────────────────────────
def sql_rag_chain(question: str) -> str:

    #generating the sql query
    sql_query_chain = create_sql_query_chain(llm, db)

    
    raw_sql = sql_query_chain.invoke({"question": question})
    sql = clean_sql(raw_sql)

    result = db.run(sql)

    answer_prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "Question: {question}\nSQL Result: {result}\n\nAnswer:")
    ])

    response = answer_prompt | llm

    return response.invoke({"question": question, "result": result}).content

# ── Test ──────────────────────────────────────────────────────
if __name__ == "__main__":
    print(sql_rag_chain("How many claims were rejected?"))
    print(sql_rag_chain("Which equipment category has most open tickets?"))