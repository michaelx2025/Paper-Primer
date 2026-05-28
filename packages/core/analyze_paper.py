import json
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

from parser import parse_paper
from extract_tables import extract_tables
from extract_figures import extract_figures
from summarize_paper import generate_precontext
from summarize_tables import summarize_tables
from summarize_figures import summarize_figures

import sys
sys.path.append(str(Path(__file__).parent.parent / "shared"))
from schemas import PaperAnalysisOutput

load_dotenv()

app = FastAPI()


class AnalyzeRequest(BaseModel):
    source: str
    output_dir: str = "outputs"
    image_scale: float = 2.0
    model: str = "gpt-4o-mini"


def analyze_paper(
    source: str,
    output_dir: str = "outputs",
    image_scale: float = 2.0,
    model: str = "gpt-4o-mini",
) -> PaperAnalysisOutput:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    parsed = parse_paper(
        source=source,
        output_dir=output_dir,
        image_scale=image_scale,
    )

    tables = extract_tables(parsed, output_dir=str(output_path / "tables"))
    figures = extract_figures(parsed, output_dir=str(output_path / "figures"))

    precontext = generate_precontext(parsed["markdown"], model=model)
    precontext_path = output_path / "precontext.md"
    precontext_path.write_text(precontext, encoding="utf-8")

    tables = summarize_tables(tables, model=model)
    figures = summarize_figures(figures, model=model)

    analysis = PaperAnalysisOutput(
        source=source,
        paper_markdown_path=parsed["paper_markdown_path"],
        precontext_path=str(precontext_path),
        analysis_json_path=str(output_path / "analysis.json"),
        tables=tables,
        figures=figures,
    )

    (output_path / "analysis.json").write_text(
        analysis.model_dump_json(indent=2),
        encoding="utf-8",
    )

    return analysis


@app.post("/analyze", response_model=PaperAnalysisOutput)
def analyze_endpoint(request: AnalyzeRequest) -> PaperAnalysisOutput:
    try:
        return analyze_paper(
            source=request.source,
            output_dir=request.output_dir,
            image_scale=request.image_scale,
            model=request.model,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
