from __future__ import annotations

import json
from typing import Any

from langgraph.graph import END, StateGraph

from agents import final_agent, general_agent, lingo_agent
from core.deps import AgentDeps
from core.state import AgentKVState, AgentState
from core.utils import get_logger
from rag.retriever import retrieve_by_type_async

logger = get_logger(__name__)


def _traits_summary(traits: dict[str, Any]) -> str:
    if not traits:
        return "warm, supportive, student-friendly"
    tone = traits.get("tone")
    style = traits.get("style")
    parts = [f"{k}: {v}" for k, v in (("tone", tone), ("style", style)) if v]
    if parts:
        return "; ".join(parts)
    return ", ".join(f"{k}: {v}" for k, v in traits.items())


def compile_chat_graph(deps: AgentDeps):
    """
    Profile (questionnaire RAG + traits) → General → Lingo (lingo RAG + LLM) → Final → END.
    database/ CSV+JSON are not read at runtime — only rag/faiss_index from scripts/build_rag.py.
    """

    async def profile_agent_node(state: AgentState) -> dict[str, str]:
        query = (state.get("user_message") or "").strip()
        logger.info("profile_agent RAG query_len=%s", len(query))

        docs = await retrieve_by_type_async(
            query,
            "questionnaire",
            k=deps.settings.rag_top_k,
            fetch_k=deps.settings.rag_similarity_fetch_k,
            settings=deps.settings,
        )
        profile_context = "\n".join(d.page_content for d in docs)
        if not profile_context.strip():
            profile_context = (
                "No questionnaire RAG hits (build index with: python scripts/build_rag.py)."
            )

        uq = state.get("questionnaire") or {}
        if uq:
            snap = json.dumps(uq, ensure_ascii=False)
            if len(snap) > 1200:
                snap = snap[:1200] + "…"
            profile_context = f"{profile_context}\n\nStored user answers: {snap}"

        user_traits = _traits_summary(dict(state.get("traits") or {}))
        out = {"profile_context": profile_context.strip(), "user_traits": user_traits}
        logger.info("profile_agent out pc_len=%s ut=%s", len(out["profile_context"]), out["user_traits"][:80])
        return out

    async def general_agent_node(state: AgentState) -> dict[str, str]:
        logger.info("general_agent in msg_len=%s", len(state.get("user_message") or ""))
        kv = AgentKVState(
            user_id=state.get("user_id") or "",
            message=state.get("user_message") or "",
            traits={},
            questionnaire={},
        )
        patch = await general_agent.run(kv, deps)
        out = {
            "mental_state": patch["mental_state"],
            "suggestions": patch["suggestions"],
            "follow_up": patch["follow_up"],
        }
        logger.info(
            "general_agent out ms=%s sg=%s fu=%s",
            len(out["mental_state"]),
            len(out["suggestions"]),
            len(out["follow_up"]),
        )
        return out

    async def lingo_agent_node(state: AgentState) -> dict[str, str]:
        query = (state.get("user_message") or "").strip()
        docs = await retrieve_by_type_async(
            query,
            "lingo",
            k=deps.settings.rag_top_k,
            fetch_k=deps.settings.rag_similarity_fetch_k,
            settings=deps.settings,
        )
        hits = [d.page_content for d in docs]
        logger.info("lingo_agent RAG hits=%s", len(hits))

        suggestions = (state.get("suggestions") or "").strip()
        if not hits:
            logger.info("lingo_agent: no lingo RAG hits, fallback to suggestions only")
            return {"lingo_style": suggestions, "rag_hits": hits}

        mental = (state.get("mental_state") or "").strip()
        draft = "\n\n".join(p for p in (mental, suggestions) if p)
        if not draft.strip():
            draft = query
        rag_blob = "\n".join(f"- {h}" for h in hits)
        kv = AgentKVState(
            user_id=state.get("user_id") or "",
            message=state.get("user_message") or "",
            traits=dict(state.get("traits") or {}),
            questionnaire={},
            academic_load=state.get("academic_load"),
            profile_context=state.get("profile_context") or "",
            user_traits=state.get("user_traits") or "",
            mental_state=mental,
            suggestions=suggestions,
            follow_up=state.get("follow_up") or "",
            rag_hits=rag_blob,
        )
        patch = await lingo_agent.run(kv, deps)
        out = {"lingo_style": patch.get("lingo_style", ""), "rag_hits": hits}
        logger.info("lingo_agent out len=%s", len(out.get("lingo_style") or ""))
        return out

    async def final_agent_node(state: AgentState) -> dict[str, str]:
        logger.info("final_agent in")
        rag_list = state.get("rag_hits") or []
        rag_str = "\n".join(rag_list) if isinstance(rag_list, list) else str(rag_list)
        kv = AgentKVState(
            user_id=state.get("user_id") or "",
            message=state.get("user_message") or "",
            traits=dict(state.get("traits") or {}),
            questionnaire=dict(state.get("questionnaire") or {}),
            academic_load=state.get("academic_load"),
            profile_context=state.get("profile_context") or "",
            user_traits=state.get("user_traits") or "",
            mental_state=state.get("mental_state") or "",
            suggestions=state.get("suggestions") or "",
            follow_up=state.get("follow_up") or "",
            rag_hits=rag_str,
            lingo_style=state.get("lingo_style") or "",
        )
        patch = await final_agent.run(kv, deps)
        out = {"final_response": patch.get("final_response", "")}
        logger.info("final_agent out len=%s", len(out.get("final_response") or ""))
        return out

    builder = StateGraph(AgentState)
    builder.add_node("profile_agent", profile_agent_node)
    builder.add_node("general_agent", general_agent_node)
    builder.add_node("lingo_agent", lingo_agent_node)
    builder.add_node("final_agent", final_agent_node)

    builder.set_entry_point("profile_agent")
    builder.add_edge("profile_agent", "general_agent")
    builder.add_edge("general_agent", "lingo_agent")
    builder.add_edge("lingo_agent", "final_agent")
    builder.add_edge("final_agent", END)

    return builder.compile()
