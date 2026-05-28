import re
from pathlib import Path


def extract_figures(parsed, output_dir="outputs/figures"):
    document = parsed["document"]
    markdown = parsed["markdown"]

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    figures = []

    for i, picture in enumerate(document.pictures):
        index = i + 1

        try:
            image = picture.get_image(document)
        except Exception:
            image = None

        if image is None:
            continue

        image_path = output_path / f"figure_{index}.png"
        image.save(image_path)

        figures.append({
            "index": index,
            "image_path": str(image_path),
            "caption": None,
            "nearby_text": None,
            "summary": None,
        })

    captions = extract_figure_captions(markdown)

    figures = merge_captions(figures, captions)

    for figure in figures:
        figure["nearby_text"] = extract_nearby_text(
            markdown,
            figure["index"]
        )

    return figures


def extract_figure_captions(markdown: str):
    pattern = r"Figure\s+(\d+)[:.]\s*(.*?)(?=\n\n|\Z)"

    matches = re.findall(pattern, markdown, re.DOTALL)

    captions = []

    for match in matches:
        figure_num = int(match[0])
        caption_text = match[1].strip()

        captions.append({
            "index": figure_num,
            "caption": caption_text
        })

    return captions


def merge_captions(figures, captions):
    for figure in figures:
        idx = figure["index"]

        matching = next(
            (c for c in captions if c["index"] == idx),
            None
        )

        if matching:
            figure["caption"] = matching["caption"]

    return figures


def extract_nearby_text(markdown: str, figure_index: int):
    target = f"Figure {figure_index}"

    idx = markdown.find(target)

    if idx == -1:
        return None

    start = max(0, idx - 1500)
    end = min(len(markdown), idx + 1500)

    return markdown[start:end]
