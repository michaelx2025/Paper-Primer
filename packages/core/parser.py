from pathlib import Path

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption


def parse_paper(source: str, output_dir: str = "outputs", image_scale: float = 2.0):
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    pipeline_options = PdfPipelineOptions()
    pipeline_options.generate_page_images = True
    pipeline_options.generate_picture_images = True
    pipeline_options.images_scale = image_scale

    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(
                pipeline_options=pipeline_options
            )
        }
    )

    result = converter.convert(source)
    document = result.document
    markdown = document.export_to_markdown()

    paper_md_path = output_path / "paper.md"
    paper_md_path.write_text(markdown, encoding="utf-8")

    return {
        "source": source,
        "result": result,
        "document": document,
        "markdown": markdown,
        "paper_markdown_path": str(paper_md_path),
        "output_dir": str(output_path),
    }