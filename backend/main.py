from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import auth, chat, collections, health

app = FastAPI(title="MediBot API")

# allow the Next.js dev frontend to call this API from the browser
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# plug in routers
app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(collections.router)
app.include_router(health.router)
