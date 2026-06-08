from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import chats, health, jobs, papers, summaries
from app.db.models import Base
from app.db.session import engine


def create_app() -> FastAPI:
    Base.metadata.create_all(bind=engine)
    app = FastAPI(title="Paper RAG Assistant")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(health.router)
    app.include_router(papers.router)
    app.include_router(chats.router)
    app.include_router(summaries.router)
    app.include_router(jobs.router)
    return app


app = create_app()
