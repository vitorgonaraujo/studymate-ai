from pathlib import Path

import fitz
from langchain_core.documents import Document


def load_pdf(file_path: str | Path) -> list[Document]:
    """
    Carrega PDF usando PyMuPDF mantendo a ordem espacial do texto.
    """

    path_str = str(file_path)

    pdf = fitz.open(path_str)

    documents = []

    for page_num, page in enumerate(pdf):

        text = page.get_text(
            "text",
            sort=True,
        )

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

    pdf.close()

    return documents