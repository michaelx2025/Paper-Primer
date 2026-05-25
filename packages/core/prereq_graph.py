import os
import json
import re
from typing import List, Literal
from pydantic import BaseModel, Field
from dotenv import load_dotenv

import networkx as nx
from docling.document_converter import DocumentConverter
from langchain_openai import ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter


load_dotenv()


# -----------------------------
# Schemas
# -----------------------------

class Concept(BaseModel):
    id: str = Field(description="Stable snake_case concept id")
    name: str
    definition: str
    difficulty: Literal["beginner", "intermediate", "advanced"]
    source_section: str


class ConceptList(BaseModel):
    concepts: List[Concept]


class DependencyEdge(BaseModel):
    prerequisite: str = Field(description="Concept id that should be understood first")
    dependent: str = Field(description="Concept id that depends on the prerequisite")
    reason: str
    confidence: float = Field(ge=0.0, le=1.0)


class EdgeList(BaseModel):
    edges: List[DependencyEdge]


# -----------------------------
# PDF / Paper loading
# -----------------------------

def load_paper_as_markdown(source: str) -> str:
    converter = DocumentConverter()
    result = converter.convert(source)
    return result.document.export_to_markdown()


def chunk_text(text: str, chunk_size: int = 4000, chunk_overlap: int = 400) -> List[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n## ", "\n### ", "\n\n", "\n", " "],
    )
    return splitter.split_text(text)


# -----------------------------
# Concept extraction
# -----------------------------

def extract_concepts_from_chunk(llm, chunk: str, max_concepts: int = 35) -> ConceptList:
    structured_llm = llm.with_structured_output(ConceptList)

    prompt = f"""
You are analyzing a research paper.

Extract up to {max_concepts} important concepts that a reader may need to understand this paper.

Rules:
- Only include concepts relevant to understanding the paper and are domain specific.
- Prefer technical concepts, methods, equations, datasets, assumptions, and evaluation ideas.
- Do not include generic words like "model", "data", or "experiment" unless paper-specific.
- Do not reference Arxiv links
- Do not include file formats like PDF, Markdown, arxiv identifier, csv, etc.
- Use stable snake_case IDs.
- Keep definitions concise.
- source_section can be inferred from headings or context.
- if possible, include an online source link for the concept definition.
- if a concept mentioned has a formula tied into it, make sure to include the formula in the definition. Use LaTeX formatting for formulas.
- Do not include information about identifiers like arxiv links, figure numbers, table numbers, or section numbers in the definition. Instead, include that information in the source_section field.
- If the concept is related to mathematics, please make sure to include the mathematical definition in the definition field, and include the latex for the formulation in the definition field as well.


Paper chunk:
{chunk}
"""

    return structured_llm.invoke(prompt)


def normalize_id(name: str) -> str:
    value = name.lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_")


def merge_concepts(concepts: List[Concept]) -> List[Concept]:
    merged = {}

    for c in concepts:
        cid = c.id or normalize_id(c.name)
        cid = normalize_id(cid)

        if cid not in merged:
            merged[cid] = Concept(
                id=cid,
                name=c.name,
                definition=c.definition,
                difficulty=c.difficulty,
                source_section=c.source_section,
            )
        else:
            existing = merged[cid]
            if len(c.definition) > len(existing.definition):
                merged[cid] = Concept(
                    id=cid,
                    name=existing.name,
                    definition=c.definition,
                    difficulty=existing.difficulty,
                    source_section=existing.source_section,
                )

    return list(merged.values())


# -----------------------------
# Edge inference
# -----------------------------

def infer_edges(llm, concepts: List[Concept]) -> EdgeList:
    structured_llm = llm.with_structured_output(EdgeList)

    concept_payload = [
        {
            "id": c.id,
            "name": c.name,
            "definition": c.definition,
            "difficulty": c.difficulty,
        }
        for c in concepts
    ]

    prompt = f"""
Given the following research-paper concepts, infer prerequisite relationships.

An edge A -> B means:
A should be understood before B.

Rules:
- Only create meaningful prerequisite edges.
- Avoid loose association edges.
- Prefer fewer, high-confidence edges.
- Do not create self-edges.
- Use only the provided concept IDs.
- confidence should be between 0 and 1.

Concepts:
{json.dumps(concept_payload, indent=2)}
"""

    return structured_llm.invoke(prompt)


# -----------------------------
# Graph construction / cleanup
# -----------------------------

def build_graph(concepts: List[Concept], edges: List[DependencyEdge], min_confidence: float = 0.7):
    G = nx.DiGraph()

    valid_ids = {c.id for c in concepts}

    for c in concepts:
        G.add_node(
            c.id,
            name=c.name,
            definition=c.definition,
            difficulty=c.difficulty,
            source_section=c.source_section,
        )

    for e in edges:
        if (
            e.confidence >= min_confidence
            and e.prerequisite in valid_ids
            and e.dependent in valid_ids
            and e.prerequisite != e.dependent
        ):
            G.add_edge(
                e.prerequisite,
                e.dependent,
                reason=e.reason,
                confidence=e.confidence,
            )

    return G


def remove_cycles(G: nx.DiGraph) -> nx.DiGraph:
    G = G.copy()
    G.remove_edges_from(nx.selfloop_edges(G))

    while True:
        cycles = list(nx.simple_cycles(G))
        if not cycles:
            break

        cycle = cycles[0]
        cycle_edges = list(zip(cycle, cycle[1:] + [cycle[0]]))

        weakest_edge = min(
            cycle_edges,
            key=lambda edge: G.edges[edge].get("confidence", 0.0),
        )

        G.remove_edge(*weakest_edge)

    return G


def get_learning_path(G: nx.DiGraph) -> List[str]:
    if not nx.is_directed_acyclic_graph(G):
        G = remove_cycles(G)

    return list(nx.topological_sort(G))


# -----------------------------
# Exports
# -----------------------------

def export_graph_json(G: nx.DiGraph, path: str):
    data = {
        "nodes": [
            {"id": node_id, **attrs}
            for node_id, attrs in G.nodes(data=True)
        ],
        "edges": [
            {"prerequisite": u, "dependent": v, **attrs}
            for u, v, attrs in G.edges(data=True)
        ],
    }

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def export_markdown(G: nx.DiGraph, path: str):
    learning_path = get_learning_path(G)

    lines = ["# Prerequisite Dependency Graph\n"]

    lines.append("## Learning Path\n")
    for i, node_id in enumerate(learning_path, start=1):
        node = G.nodes[node_id]
        lines.append(f"{i}. **{node['name']}** — {node['definition']}")

    lines.append("\n## Concept Dependencies\n")

    for node_id in learning_path:
        node = G.nodes[node_id]
        prereqs = list(G.predecessors(node_id))

        lines.append(f"\n### {node['name']}")
        lines.append(f"- **Difficulty:** {node['difficulty']}")
        lines.append(f"- **Definition:** {node['definition']}")
        lines.append(f"- **Source section:** {node['source_section']}")

        if prereqs:
            lines.append("- **Prerequisites:**")
            for p in prereqs:
                edge = G.edges[p, node_id]
                lines.append(
                    f"  - {G.nodes[p]['name']} "
                    f"(confidence: {edge['confidence']:.2f}) — {edge['reason']}"
                )
        else:
            lines.append("- **Prerequisites:** None")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


# -----------------------------
# Main pipeline
# -----------------------------

def build_prerequisite_graph(source: str):
    llm = ChatOpenAI(
        model="gpt-4.1-mini",
        temperature=0,
    )

    print("Loading paper...")
    markdown = load_paper_as_markdown(source)

    print("Chunking paper...")
    chunks = chunk_text(markdown)

    print("Extracting concepts...")
    all_concepts = []

    # Limit early for MVP. Increase later.
    for chunk in chunks[:12]:
        result = extract_concepts_from_chunk(llm, chunk)
        all_concepts.extend(result.concepts)

    concepts = merge_concepts(all_concepts)

    print(f"Extracted {len(concepts)} unique concepts.")

    print("Inferring prerequisite edges...")
    edge_result = infer_edges(llm, concepts)

    print(f"Inferred {len(edge_result.edges)} raw edges.")

    print("Building graph...")
    G = build_graph(concepts, edge_result.edges, min_confidence=0.7)

    print("Removing cycles...")
    G = remove_cycles(G)

    print(f"Final graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges.")

    return G


if __name__ == "__main__":
    source = "https://arxiv.org/abs/2605.23829"

    G = build_prerequisite_graph(source)

    os.makedirs("outputs", exist_ok=True)

    export_graph_json(G, "outputs/prereq_graph.json")
    export_markdown(G, "outputs/prereq_graph.md")
    nx.write_graphml(G, "outputs/prereq_graph.graphml")

    print("Done.")
    print("Wrote:")
    print("- outputs/prereq_graph.json")
    print("- outputs/prereq_graph.md")
    print("- outputs/prereq_graph.graphml")