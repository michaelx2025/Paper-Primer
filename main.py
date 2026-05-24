from docling.document_converter import DocumentConverter
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model

model = init_chat_model(
    "openai:gpt-5.4.nano",
    temperature=0.5,
    timeout=300,
    max_tokens=25000,
)

SYSTEM_PROMPT = "You are generating a pre-reading context document for a research paper. " \
"Given the paper text below, produce: 1. Paper Snapshot 2. Prerequisite Concepts 3. Key Terms 4. Problem Background 5. Method Preview 6. Reading Guide" \
"Keep it concise, beginner-friendly, and grounded only in the paper text. Please make sure to give a proper explanation regarding the terminology and concepts."

def main():
    source = "https://arxiv.org/pdf/2206.01062"
    converter = DocumentConverter()
    result = converter.convert(source)
    markdown = result.document.export_to_markdown()
    print(markdown)

if __name__ == "__main__":#
    main()