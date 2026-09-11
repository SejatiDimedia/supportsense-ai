import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Dict, Any

@dataclass
class DocumentChunk:
    id: str
    text: str
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class MarkdownSectionChunker:
    """
    Section-aware Markdown chunker that preserves heading context
    and splits oversized sections cleanly using paragraph/sentence boundaries.
    """
    def __init__(self, max_chunk_chars: int = 1500, overlap_chars: int = 200):
        self.max_chunk_chars = max_chunk_chars
        self.overlap_chars = overlap_chars

    def split_text_with_overlap(self, text: str, section_title: str) -> List[str]:
        if len(text) <= self.max_chunk_chars:
            return [text.strip()]

        # Split by double newline (paragraphs) first
        paragraphs = text.split("\n\n")
        chunks = []
        current_chunk = f"### {section_title}\n" if section_title else ""

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            if len(current_chunk) + len(para) + 2 <= self.max_chunk_chars:
                current_chunk += ("\n\n" if current_chunk else "") + para
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    # Create overlap from end of current chunk
                    overlap = current_chunk[-self.overlap_chars:] if len(current_chunk) > self.overlap_chars else ""
                    current_chunk = f"### {section_title} (cont.)\n{overlap}\n\n{para}"
                else:
                    # Single paragraph exceeds max_chunk_chars, split on sentence boundary
                    sentences = re.split(r'(?<=[.?!])\s+', para)
                    sub_chunk = ""
                    for s in sentences:
                        if len(sub_chunk) + len(s) + 1 <= self.max_chunk_chars:
                            sub_chunk += (" " if sub_chunk else "") + s
                        else:
                            if sub_chunk:
                                chunks.append(sub_chunk.strip())
                            sub_chunk = s
                    if sub_chunk:
                        current_chunk = sub_chunk

        if current_chunk and current_chunk.strip():
            chunks.append(current_chunk.strip())

        return chunks

    def chunk_markdown(self, content: str, source_name: str) -> List[DocumentChunk]:
        """
        Parses markdown content by headings (#, ##, ###) and creates DocumentChunk items.
        """
        lines = content.splitlines()
        sections = []
        current_heading = "Overview"
        current_lines = []

        heading_pattern = re.compile(r'^(#{1,3})\s+(.+)$')

        for line in lines:
            match = heading_pattern.match(line)
            if match:
                if current_lines:
                    section_body = "\n".join(current_lines).strip()
                    if section_body:
                        sections.append((current_heading, section_body))
                    current_lines = []
                current_heading = match.group(2).strip()
            else:
                current_lines.append(line)

        if current_lines:
            section_body = "\n".join(current_lines).strip()
            if section_body:
                sections.append((current_heading, section_body))

        # Build chunks with metadata
        chunks: List[DocumentChunk] = []
        chunk_idx = 0

        for heading, body in sections:
            # Prefix section title to body for strong semantic retrieval
            full_section_text = f"## {heading}\n{body}" if not body.startswith("##") else body
            sub_chunks = self.split_text_with_overlap(full_section_text, heading)

            for sub_text in sub_chunks:
                clean_source = Path(source_name).name
                chunk_id = f"{clean_source}_{chunk_idx:03d}"
                metadata = {
                    "source": clean_source,
                    "section": heading,
                    "chunk_index": chunk_idx,
                    "char_count": len(sub_text),
                }
                chunks.append(DocumentChunk(id=chunk_id, text=sub_text, metadata=metadata))
                chunk_idx += 1

        return chunks

    def chunk_file(self, file_path: Path) -> List[DocumentChunk]:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        return self.chunk_markdown(content, file_path.name)
