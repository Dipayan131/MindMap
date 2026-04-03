# MindMap backend architecture

## Chat pipeline

1. **Parallel:** `profile_agent` and `intelligence_agent` read the same initial `AgentKVState` (message, traits, questionnaire) and produce disjoint keys.
2. **Merge** into one KV state.
3. **Milvus:** embed the user message; semantic search populates `milvus_hits`.
4. **Sequential:** `lingo_agent` (uses `milvus_hits` + intelligence draft) → `response_agent` (final user-visible string).

## State

`AgentKVState` (`app/core/state_manager.py`) is the contract between agents. Each agent returns a `dict` patch; `StateManager.merge` applies updates.

## Prompts

All agent instructions live in `app/core/prompts.py` with `PROMPTS_VERSION` for traceability.

## Langflow vs OpenAI

If `LANGFLOW_*_FLOW_ID` and Langflow URL/key are set for a given step, that step calls Langflow’s `/api/v1/run/{FLOW_ID}` with the composed prompt. Otherwise the step uses the OpenAI API (`OPENAI_API_KEY`).
