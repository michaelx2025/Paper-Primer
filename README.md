# Paper Precontext

An AI-powered research paper reading assistant that generates structured “Precontext” documents to help readers understand a paper before diving into the full text.

The system parses academic papers, extracts key concepts and figures, summarizes important sections, and generates prerequisite explanations, terminology guides, and reading recommendations.

---

## Features

- PDF and arXiv paper ingestion
- Structured research paper summarization
- Prerequisite concept extraction
- Key terminology explanations
- Figure and table extraction
- Reading guides for difficult papers
- Markdown export
- Interactive paper assistance (planned)
- Hover-based keyword definitions inside papers (planned)

---

## Example Output

Given a research paper, the system generates:

- Paper Snapshot
- Problem Background
- Method Overview
- Prerequisite Knowledge
- Key Terms and Definitions
- Important Figures Explained
- Reading Recommendations
- Section-by-Section Guidance

---

## Architecture

```text
PDF / arXiv Paper
        ↓
    Docling Parser
        ↓
Structured Paper Extraction
        ↓
LLM Processing Pipeline
        ↓
Precontext Generation
        ↓
Frontend Viewer / Export
```

---

## Tech Stack

### Backend

- Python
- FastAPI
- LangChain
- Docling

### Frontend

- Next.js
- React
- TailwindCSS
- PDF.js / react-pdf

### AI / NLP

- OpenAI API / Gemini API
- LangChain pipelines
- Figure understanding (planned)

---

## Project Structure

```text
paper-precontext/
├── apps/
│   ├── web/          # Next.js frontend
│   └── api/          # FastAPI backend
│
├── packages/
│   ├── core/         # Core parsing + AI pipeline
│   └── shared/       # Shared schemas/types
│
│
└── README.md
```

---

## Current Goals

### MVP

- [ ] Parse research papers from PDF/arXiv
- [ ] Generate structured summaries
- [ ] Extract prerequisite concepts
- [ ] Generate terminology explanations

### Future Features

- [ ] Figure and table understanding
- [ ] Interactive PDF overlays
- [ ] Hover-based keyword explanations
- [ ] Citation-aware Q&A
- [ ] Multi-paper knowledge graphs
- [ ] Personalized reading levels
- [ ] Research assistant workflows

---

## Getting Started

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Get Open AI API Key
[Open AI Website](https://openai.com/api/pricing/)
### Run Example

```bash
python main.py
```

### Example

```python
from docling.document_converter import DocumentConverter

source = "https://arxiv.org/pdf/2206.01062"

converter = DocumentConverter()
result = converter.convert(source)

markdown = result.document.export_to_markdown()

print(markdown[:5000])
```

---

## Vision

The long-term goal of this project is to make difficult academic papers significantly easier to approach by generating interactive contextual guidance directly alongside the paper itself.

Instead of reading papers completely cold, users receive a structured understanding of:

- what the paper is solving
- what background knowledge is required
- which concepts matter most
- how to interpret figures and results
- what sections deserve the most attention

The project aims to function as an intelligent research companion for students, engineers, and researchers.