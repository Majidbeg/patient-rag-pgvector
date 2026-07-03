"""
Handles reading PDF files and pulling out raw text plus a couple of
structured fields (MRN, patient name) via simple regex matching.

If your PDFs have a consistent layout, extend extract_fields() to pull
out more structured fields (diagnosis, department, etc.) so they can be
stored in dedicated columns for exact-match filtering alongside vector search.
"""
import re
from pypdf import PdfReader


def extract_text(pdf_path: str) -> str:
    reader = PdfReader(pdf_path)
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def extract_fields(text: str) -> dict:
    def find(pattern):
        m = re.search(pattern, text)
        return m.group(1).strip() if m else None

    return {
        "mrn": find(r"MRN:\s*(\S+)"),
        "patient_name": find(r"Patient Name:\s*(.+)"),
        "department": find(r"Department:\s*(.+)"),
        "diagnosis": find(r"Diagnosis:\s*(.+)"),
    }
