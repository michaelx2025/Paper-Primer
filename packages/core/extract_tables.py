from pathlib import Path


def extract_tables(parsed, output_dir: str = "outputs/tables"):
    document = parsed["document"]

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    tables = []

    for i, table in enumerate(document.tables):
        index = i + 1

        markdown = table.export_to_markdown(document)
        html = table.export_to_html(document)

        csv_path = None

        try:
            df = table.export_to_dataframe(document)
            csv_file = output_path / f"table_{index}.csv"
            df.to_csv(csv_file, index=False)
            csv_path = str(csv_file)
        except Exception:
            pass

        html_path = output_path / f"table_{index}.html"
        html_path.write_text(html, encoding="utf-8")

        tables.append({
            "index": index,
            "markdown": markdown,
            "csv_path": csv_path,
            "html_path": str(html_path),
            "summary": None,
        })

    return tables