from pydantic import BaseModel, Field


class SummaryRead(BaseModel):
    paper_id: str
    summary: str
    citations: list[dict]


class CompareRequest(BaseModel):
    paper_ids: list[str] = Field(min_length=2, max_length=5)
    dimensions: list[str] = Field(
        default_factory=lambda: ["研究问题", "方法", "数据集", "指标", "主要结论", "局限性"]
    )


class CompareRead(BaseModel):
    comparison: str
    citations: list[dict]
