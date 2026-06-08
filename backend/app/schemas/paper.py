from pydantic import BaseModel, ConfigDict


class PaperRead(BaseModel):
    id: str
    title: str
    authors: list[str]
    abstract: str
    year: int | None
    venue: str
    file_name: str
    status: str
    error_message: str

    model_config = ConfigDict(from_attributes=True)


class ChunkRead(BaseModel):
    id: str
    paper_id: str
    chunk_index: int
    page_start: int
    page_end: int
    section: str
    text: str
    token_count: int

    model_config = ConfigDict(from_attributes=True)
