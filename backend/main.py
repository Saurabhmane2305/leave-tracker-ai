from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from database import engine
from models import Base
from routers import auth, leaves, users, calendar, ai

# Create all tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Leave & Time-Off Tracker",
    description="Unico Connect Internal Leave Management System",
    version="1.0.0",
)

# CORS — allow React dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router)
app.include_router(leaves.router)
app.include_router(users.router)
app.include_router(calendar.router)
app.include_router(ai.router)


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "message": "Leave Tracker API is running 🚀"}


@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy"}