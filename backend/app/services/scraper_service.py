"""
Placeholder for KGP scraping / cleaning orchestration.

Wire `data_pipeline/scraping/kgp_scraper.py` outputs into Milvus via
`data_pipeline/milvus_ingestion/ingest_tables.py` in batch jobs — not on the
hot chat path.
"""

from __future__ import annotations

from app.utils.logger import get_logger

logger = get_logger(__name__)


def note_scrape_stub() -> None:
    logger.debug("scraper_service: batch scraping is a pipeline concern, not invoked per chat")
