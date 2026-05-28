import os

from dotenv import load_dotenv
from openai import OpenAI



def summarize_figure_from_caption(figure, model: str = "gpt-4o-mini") -> str:
    load_dotenv()
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    caption = figure.get("caption") or "No caption was extracted."
    nearby_text = figure.get("nearby_text") or "No nearby text was extracted."

    prompt = f"""
Explain this research paper figure for a reader.

Use the caption and nearby text. Do not invent visual details that are not provided.

Focus on:
- what the figure likely shows
- why it matters
- how it helps understand the paper

Caption:
{caption}

Nearby text:
{nearby_text}
"""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You explain research paper figures clearly and cautiously."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2,
    )

    return response.choices[0].message.content


def summarize_figures(figures, model: str = "gpt-4o-mini"):
    summarized = []

    for figure in figures:
        figure = dict(figure)
        figure["summary"] = summarize_figure_from_caption(figure, model=model)
        summarized.append(figure)

    return summarized