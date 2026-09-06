from fastapi import FastAPI
from backend.routers import auth, chat, collections, health

app = FastAPI(title="MediBot API")

# plug in routers
app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(collections.router)
app.include_router(health.router)
