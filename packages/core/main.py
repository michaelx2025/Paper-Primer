import argparse
from dotenv import load_dotenv
from analyze_paper import analyze_paper

def main():
    load_dotenv()

    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, help="PDF path or URL")
    parser.add_argument("--output-dir", default="outputs")
    parser.add_argument("--image-scale", type=float, default=2.0)
    parser.add_argument("--model", default="gpt-4o-mini")

    args = parser.parse_args()

    result = analyze_paper(
        source=args.source,
        output_dir=args.output_dir,
        image_scale=args.image_scale,
        model=args.model,
    )

    print(f"Paper Markdown: {result.paper_markdown_path}")
    print(f"Precontext: {result.precontext_path}")
    print(f"Analysis JSON: {result.analysis_json_path}")
    print(f"Tables extracted: {len(result.tables)}")
    print(f"Figures extracted: {len(result.figures)}")


if __name__ == "__main__":
    main()
