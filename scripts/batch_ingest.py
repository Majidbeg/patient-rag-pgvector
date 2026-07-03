"""
One-time bulk loader for your existing 50 PDFs. Bypasses the HTTP API
and calls the ingest pipeline directly for speed.

Usage:
    python -m scripts.batch_ingest /path/to/pdf/folder
"""
import sys
import glob
import time

from app.services.ingest_service import ingest_pdf


def main(folder: str):
    pdf_files = sorted(glob.glob(f"{folder}/*.pdf"))
    if not pdf_files:
        print(f"No PDFs found in {folder}")
        return

    print(f"Found {len(pdf_files)} PDFs. Starting ingest...\n")

    succeeded, failed = 0, 0
    start = time.time()

    for path in pdf_files:
        try:
            result = ingest_pdf(path)
            print(f"[OK]   {path} -> patient_id={result['patient_id']} "
                  f"mrn={result['mrn']} chunks={result['chunks_created']}")
            succeeded += 1
        except Exception as e:
            print(f"[FAIL] {path} -> {e}")
            failed += 1

    elapsed = time.time() - start
    print(f"\nDone in {elapsed:.1f}s — {succeeded} succeeded, {failed} failed.")

    if succeeded > 0:
        print(
            "\nNow build the vector index for fast search:\n"
            "  CREATE INDEX ON document_chunks USING hnsw (embedding vector_cosine_ops);"
        )


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python -m scripts.batch_ingest /path/to/pdf/folder")
        sys.exit(1)
    main(sys.argv[1])
