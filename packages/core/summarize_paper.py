from openai import OpenAI
import os
from dotenv import load_dotenv
from rich.markdown import Markdown



def generate_precontext(markdown: str, model: str = "gpt-4o-mini") -> str:
    load_dotenv()
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    trimmed_markdown = markdown[:60000]

    prompt = f"""
You are generating a pre-reading guide for a research paper.

Create a structured Precontext document with the following sections:

# Paper Snapshot
- Title if available
- Field / topic
- One-paragraph summary
- Intended reader level

# Problem Background
Explain the problem the paper is addressing and why it matters.

# Prerequisite Concepts
List the concepts a reader should understand before reading the paper.
For each concept, include a concise explanation.

# Key Terms
Define important technical terms from the paper.

# Method Overview
Explain the core method at a high level.

# Results / Evaluation Context
Explain what the experiments or results are trying to show.

# Reading Guide
Tell the reader which sections to focus on, what to skim, and what questions to keep in mind.

Ground the answer only in the paper text.

Paper text:
{trimmed_markdown}
"""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You are an expert research paper reading assistant."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2,
    )

    return response.choices[0].message.content