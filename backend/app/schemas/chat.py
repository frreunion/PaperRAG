from pydantic import BaseModel, Field


class ChatCreate(BaseModel):
    paper_ids: list[str] = Field(default_factory=list)
    title: str = "Paper discussion"


class ChatRead(BaseModel):
    id: str
    title: str
    scope: dict


class QuestionCreate(BaseModel):
    question: str = Field(min_length=1)


class CitationRead(BaseModel):
    paper_id: str
    paper_title: str
    chunk_id: str
    page_start: int
    page_end: int
    section: str
    quote: str


class AnswerRead(BaseModel):
    answer: str
    citations: list[CitationRead]
