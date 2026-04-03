from __future__ import annotations

import json
from typing import Any

from pymilvus import MilvusClient

from app.core.config import Settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

# text-embedding-3-small default dimension
DEFAULT_EMBEDDING_DIM = 1536


class MilvusService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client: MilvusClient | None = None
        self._connected = False
        self.collection_created_this_boot = False
        self._give_up = False

    def connect(self) -> None:
        if self._connected or self._give_up:
            return
        try:
            kwargs: dict[str, Any] = {
                "uri": self._settings.milvus_uri,
                "timeout": self._settings.milvus_connect_timeout,
            }
            if self._settings.milvus_token:
                kwargs["token"] = self._settings.milvus_token
            self._client = MilvusClient(**kwargs)
            self.collection_created_this_boot = self._ensure_collection()
            self._connected = True
            logger.info("Milvus connected (%s)", self._settings.milvus_uri)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Milvus unavailable: %s", exc)
            self._client = None
            self._connected = False
            self.collection_created_this_boot = False
            self._give_up = True

    def _ensure_collection(self) -> bool:
        """Returns True if the collection was created in this call."""
        assert self._client is not None
        name = self._settings.milvus_collection_kgp
        if self._client.has_collection(collection_name=name):
            return False
        self._client.create_collection(
            collection_name=name,
            dimension=DEFAULT_EMBEDDING_DIM,
            auto_id=True,
            enable_dynamic_field=True,
        )
        logger.info("Created Milvus collection %s", name)
        return True

    async def seed_default_corpus(self, embed_fn) -> None:
        """embed_fn: async (str) -> list[float]. Inserts starter KGP lines once per new collection."""
        self.connect()
        if not self._client or not self.collection_created_this_boot:
            return
        name = self._settings.milvus_collection_kgp
        samples = [
            {"text": "Hall 3 mess line hits different during endsems.", "tags": "stress,food"},
            {"text": "Nalanda lawns — go touch grass between assignments.", "tags": "coping,campus"},
            {"text": "Tempo shouts at 2 am — you're not alone if sleep is messy.", "tags": "sleep,social"},
            {"text": "ERP woes / registration stress — break it into tiny checklist steps.", "tags": "academic"},
            {"text": "Talk to your hall sec or mentor-of-students if homesick.", "tags": "support"},
        ]
        data: list[dict[str, Any]] = []
        for row in samples:
            vec = await embed_fn(row["text"])
            if len(vec) != DEFAULT_EMBEDDING_DIM:
                logger.warning("Embedding dim mismatch; skip Milvus seed")
                return
            data.append({"vector": vec, "text": row["text"], "tags": row["tags"]})
        self._client.insert(collection_name=name, data=data)
        logger.info("Seeded %d KGP lingo rows into Milvus", len(data))

    def search_lingo(self, query_vector: list[float], top_k: int | None = None) -> str:
        self.connect()
        if not self._client:
            return ""
        k = top_k or self._settings.milvus_top_k
        name = self._settings.milvus_collection_kgp
        try:
            res = self._client.search(
                collection_name=name,
                data=[query_vector],
                limit=k,
                output_fields=["text", "tags"],
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("Milvus search failed: %s", exc)
            return ""
        hits = res[0] if res else []
        lines = []
        for h in hits:
            entity = h.get("entity") or {}
            text = entity.get("text", "")
            tags = entity.get("tags", "")
            lines.append(f"- {text} ({tags})")
        return "\n".join(lines)
