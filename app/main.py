import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routers import users, auth, resume
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="ResumeGPT API")

# CORS configuration
origins = [
    "http://localhost:3000",
    "http://localhost:8000",
    "http://localhost",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(resume.router)

@app.get("/")
async def read_root():
    return {"message": "Welcome to ResumeGPT API"}

# ✅ Async function to create tables before the app starts
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# ✅ Run the async table creation before app starts
@app.on_event("startup")
async def startup_event():
    await create_tables()


# Vercel expects ASGI-compatible callable
def handler():
    return app