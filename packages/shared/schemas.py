from pydantic import BaseModel
from typing import Optional, List


class TableOutput(BaseModel):
    index: int
    markdown: str
    csv_path: Optional[str] = None
    html_path: Optional[str] = None
    summary: Optional[str] = None


class FigureOutput(BaseModel):
    index: int
    image_path: str
    caption: Optional[str] = None
    nearby_text: Optional[str] = None
    summary: Optional[str] = None


class PaperAnalysisOutput(BaseModel):
    source: str
    paper_markdown_path: str
    precontext_path: str
    analysis_json_path: str
    tables: List[TableOutput]
    figures: List[FigureOutput]