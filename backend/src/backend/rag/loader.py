from pathlib import Path

import fitz
from langchain_core.documents import Document


def load_pdf(file_path: str | Path) -> list[Document]:
    path_str = str(file_path)
    documents = []
    with fitz.open(path_str) as pdf:
        for page_num, page in enumerate(pdf):
            text = page.get_text("text", sort=True)
            if not text.strip():
                continue
            documents.append(
                Document(
                    page_content=text,
                    metadata={
                        "source": path_str,
                        "page": page_num,
                        "page_label": page_num + 1,
                        "total_pages": len(pdf),
                    },
                )
            )
    return documents
