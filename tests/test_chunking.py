import pytest
from pathlib import Path
from app.rag.chunking import MarkdownSectionChunker, DocumentChunk

def test_chunk_markdown_structure():
    markdown_content = """# Company Handbook
## Section 1: Overview
This is the general overview of our company.

## Section 2: Vacation Policy
Employees get 20 days paid time off per year.
Requests must be submitted 2 weeks in advance.
"""
    chunker = MarkdownSectionChunker(max_chunk_chars=500, overlap_chars=50)
    chunks = chunker.chunk_markdown(markdown_content, "handbook.md")

    assert len(chunks) >= 2
    assert chunks[0].metadata["source"] == "handbook.md"
    assert "Overview" in chunks[0].metadata["section"]
    assert "Vacation Policy" in chunks[1].metadata["section"]
    assert "paid time off" in chunks[1].text

def test_chunk_real_docs():
    docs_dir = Path("data/docs")
    chunker = MarkdownSectionChunker(max_chunk_chars=1200, overlap_chars=150)

    total_chunks = []
    for doc in docs_dir.glob("*.md"):
        chunks = chunker.chunk_file(doc)
        assert len(chunks) > 0
        for c in chunks:
            assert c.id.startswith(doc.name)
            assert "source" in c.metadata
            assert "section" in c.metadata
            assert len(c.text) > 0
        total_chunks.extend(chunks)

    # We should have a good number of chunks across the 3 docs
    assert len(total_chunks) >= 5
