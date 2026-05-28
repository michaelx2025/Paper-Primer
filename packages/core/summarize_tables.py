import os

from dotenv import load_dotenv
from openai import OpenAI


def summarize_table(table, model: str = "gpt-4o-mini") -> str:
    load_dotenv()
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    prompt = f"""
Explain this research paper table for a reader.

Focus on:
- what the table measures
- what the rows and columns likely represent
- the main takeaway
- why it matters for understanding the paper

Table:
{table["markdown"][:12000]}
"""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You explain research paper tables clearly and concisely."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2,
    )

    return response.choices[0].message.content


def summarize_tables(tables, model: str = "gpt-4o-mini"):
    summarized = []

    for table in tables:
        table = dict(table)

        if table.get("markdown"):
            table["summary"] = summarize_table(table, model=model)

        summarized.append(table)

    return summarized