"""Normalize scraped text rows before embedding + Milvus insert (batch job)."""


def clean_text(text: str) -> str:
    return " ".join((text or "").split())
