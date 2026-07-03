"""
Splits long text into overlapping chunks so embeddings stay within
model context limits and retrieval granularity stays useful.

Most single-page patient records will return as a single chunk since
they're well under max_chars.
"""


def chunk_text(text: str, max_chars: int = 1500, overlap: int = 200) -> list[str]:
    text = text.strip()
    if len(text) <= max_chars:
        return [text]

    chunks = []
    start = 0
    while start < len(text):
        end = start + max_chars
        chunks.append(text[start:end])
        start = end - overlap
    return chunks
