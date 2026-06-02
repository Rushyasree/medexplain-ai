from __future__ import annotations

from pypdf import PdfReader

from modules.config import settings


def extract_text_from_pdf(file) -> str:
    size_mb = len(file.getvalue()) / (1024 * 1024)
    if size_mb > settings.max_pdf_mb:
        raise ValueError(f"PDF is too large. Maximum allowed size is {settings.max_pdf_mb} MB.")

    reader = PdfReader(file)
    if reader.is_encrypted:
        raise ValueError("Encrypted PDFs are not supported yet.")

    text_parts = []
    for page in reader.pages:
        text_parts.append(page.extract_text() or "")
    return "\n".join(text_parts).strip()
