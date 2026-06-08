from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.models import ChatMessage, ChatSession, Paper, PaperChunk
from app.db.session import get_db
from app.schemas.chat import AnswerRead, ChatCreate, ChatRead, QuestionCreate
from app.services.embedding import FakeEmbeddingClient
from app.services.rag import FakeLLMClient, answer_question
from app.services.retrieval import rank_chunks

router = APIRouter(prefix="/api/chats", tags=["chats"])


@router.post("", response_model=ChatRead)
def create_chat(payload: ChatCreate, db: Session = Depends(get_db)) -> ChatRead:
    session = ChatSession(title=payload.title, scope={"paper_ids": payload.paper_ids})
    db.add(session)
    db.commit()
    db.refresh(session)
    return ChatRead(id=session.id, title=session.title, scope=session.scope)


@router.post("/{session_id}/messages", response_model=AnswerRead)
def ask_question(
    session_id: str, payload: QuestionCreate, db: Session = Depends(get_db)
) -> dict:
    session = db.get(ChatSession, session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Chat session not found")
    paper_ids = session.scope.get("paper_ids") or []
    statement = select(PaperChunk, Paper.title).join(Paper, Paper.id == PaperChunk.paper_id)
    if paper_ids:
        statement = statement.where(PaperChunk.paper_id.in_(paper_ids))
    rows = db.execute(statement).all()
    chunks = []
    for chunk, paper_title in rows:
        chunks.append(
            {
                "id": chunk.id,
                "paper_id": chunk.paper_id,
                "paper_title": paper_title,
                "text": chunk.text,
                "page_start": chunk.page_start,
                "page_end": chunk.page_end,
                "section": chunk.section,
                "embedding": chunk.embedding,
            }
        )
    embedding = FakeEmbeddingClient(dim=get_settings().embedding_dim)
    retrieved = rank_chunks(payload.question, chunks, embedding, top_k=get_settings().default_top_k)
    result = answer_question(payload.question, retrieved, FakeLLMClient())
    db.add(ChatMessage(session_id=session.id, role="user", content=payload.question, citations=[]))
    db.add(
        ChatMessage(
            session_id=session.id,
            role="assistant",
            content=result["answer"],
            citations=result["citations"],
        )
    )
    db.commit()
    return result
