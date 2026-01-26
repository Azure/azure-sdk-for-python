
import json
import os
import time
from dataclasses import dataclass
from typing import Any, AsyncIterable, AsyncIterator, Dict, List, TypedDict

from dotenv import load_dotenv
from langgraph.graph import END, START, StateGraph
from openai import OpenAI, OpenAIError

from azure.ai.agentserver.core.models import Response, ResponseStreamEvent
from azure.ai.agentserver.langgraph import LanggraphRunContext, from_langgraph
from azure.ai.agentserver.langgraph.models.response_api_default_converter import ResponseAPIDefaultConverter
from azure.ai.agentserver.langgraph.models.response_api_request_converter import ResponseAPIRequestConverter

load_dotenv()

API_KEY = os.environ.get("AZURE_OPENAI_API_KEY")
BASE_URL = os.environ.get("AZURE_OPENAI_ENDPOINT") + "openai/v1"
DEPLOYMENT = os.environ.get("AZURE_AI_MODEL_DEPLOYMENT_NAME")  # optional override
DEFAULT_MODEL = "gpt-4.1-mini"


# ---------------------------------------------------------------------------
# Simple in-memory knowledge base (replace with real vector DB in production)
# ---------------------------------------------------------------------------
@dataclass
class KBEntry:
    id: str
    text: str
    tags: List[str]


KNOWLEDGE_BASE: List[KBEntry] = [
    KBEntry(
        id="doc1",
        text="LangGraph enables stateful AI workflows via graphs of nodes.",
        tags=["langgraph", "workflow"],
    ),
    KBEntry(
        id="doc2",
        text="Retrieval augmented generation improves answer grounding by injecting documents.",
        tags=["rag", "retrieval", "grounding"],
    ),
    KBEntry(
        id="doc3",
        text="Streaming responses send partial model outputs for lower latency user experience.",
        tags=["streaming", "latency"],
    ),
]


# ---------------------------------------------------------------------------
# LangGraph State definition
# ---------------------------------------------------------------------------
class RAGState(TypedDict, total=False):
    query: str
    messages: List[Dict[str, Any]]  # simplified message records
    needs_retrieval: bool
    retrieved: List[Dict[str, Any]]  # selected documents
    answer_parts: List[str]  # incremental answer assembly
    final_answer: str  # final answer text
    _stream_events: List[Any]  # buffered upstream model delta events (if any)
    stream: bool  # whether streaming was requested


# ---------------------------------------------------------------------------
# Utility: naive keyword scoring retrieval
# ---------------------------------------------------------------------------
KEYWORDS = {
    "langgraph": ["langgraph", "graph"],
    "retrieval": ["retrieval", "rag", "ground"],
    "stream": ["stream", "latency", "partial"],
}


def retrieve_docs(question: str, k: int = 2) -> List[Dict[str, Any]]:
    scores: List[tuple[float, KBEntry]] = []
    lower_q = question.lower()
    for entry in KNOWLEDGE_BASE:
        score = 0
        for token in entry.tags:
            if token in lower_q:
                score += 2
        for kw_group in KEYWORDS.values():
            for kw in kw_group:
                if kw in lower_q and kw in entry.text.lower():
                    score += 1
        if score > 0:
            scores.append((score, entry))
    scores.sort(key=lambda t: t[0], reverse=True)
    return [{"id": e.id, "text": e.text, "score": s} for s, e in scores[:k]]


# ---------------------------------------------------------------------------
# Custom Converter
# ---------------------------------------------------------------------------
class RAGRequestConverter(ResponseAPIRequestConverter):
    """Converter implementing mini RAG logic."""

    def __init__(self, context: LanggraphRunContext):
        self.context = context

    def convert(self) -> dict:
        req = self.context.agent_run.request
        user_input = req.get("input")
        if isinstance(user_input, list):
            for item in user_input:
                if isinstance(item, dict) and item.get("type") in (
                    "message",
                    "input_text",
                ):
                    user_input = item.get("content") or user_input
                    break
        if isinstance(user_input, list):
            user_input = " ".join(str(x) for x in user_input)
        prompt = str(user_input or "")
        messages = []
        instructions = req.get("instructions")
        if instructions and isinstance(instructions, str):
            messages.append({"role": "system", "content": instructions})
        messages.append({"role": "user", "content": prompt})
        res = {
            "query": prompt,
            "messages": messages,
            "needs_retrieval": False,
            "retrieved": [],
            "answer_parts": [],
            "stream": False,
        }
        print("initial state:", res)
        return res
    

class RAGStateConverter(ResponseAPIDefaultConverter):
    """Converter implementing mini RAG logic (non‑streaming only)."""
    def __init__(self, graph: StateGraph):
        super().__init__(graph=graph,
                         create_request_converter=lambda context: RAGRequestConverter(context))

    def get_stream_mode(self, context: LanggraphRunContext) -> str:  # noqa: D401
        if context.agent_run.request.get("stream", False):  # type: ignore[attr-defined]
            raise NotImplementedError("Streaming not supported in this sample.")
        return "values"

    async def convert_response_non_stream(self, state: Any, context: LanggraphRunContext) -> Response:
        final_answer = state.get("final_answer") or "(no answer generated)"
        print(f"convert state to response, state: {state}")
        citations = state.get("retrieved", [])
        output_item = {
            "type": "message",
            "role": "assistant",
            "content": [
                {
                    "type": "output_text",
                    "text": final_answer,
                    "annotations": [
                        {
                            "type": "citation",
                            "doc_id": c.get("id"),
                            "score": c.get("score"),
                        }
                        for c in citations
                    ],
                }
            ],
        }
        base = {
            "object": "response",
            "id": context.agent_run.response_id,
            "agent": context.agent_run.get_agent_id_object(),
            "conversation": context.agent_run.get_conversation_object(),
            "status": "completed",
            "created_at": int(time.time()),
            "output": [output_item],
        }
        return Response(**base)

    async def convert_response_stream(  # noqa: D401
        self,
        stream_state: AsyncIterator[Dict[str, Any] | Any],
        context: LanggraphRunContext,
    ) -> AsyncIterable[ResponseStreamEvent]:
        raise NotImplementedError("Streaming not supported in this sample.")


# ---------------------------------------------------------------------------
# Graph Nodes
# ---------------------------------------------------------------------------


def _normalize_query(val: Any) -> str:
    """Extract a lowercase text query from varied structures.

    Accepts:
      * str
      * dict with 'content' or 'text'
      * list of mixed items (recursively extracts first textual segment)
    Falls back to JSON stringification for unknown structures.
    """
    if isinstance(val, str):
        return val.strip().lower()
    if isinstance(val, dict):
        for k in ("content", "text", "value"):
            v = val.get(k)
            if isinstance(v, str) and v.strip():
                return v.strip().lower()
        # flatten simple dict string values
        parts = [str(v) for v in val.values() if isinstance(v, (str, int, float))]
        if parts:
            return " ".join(parts).lower()
    if isinstance(val, list):
        for item in val:  # take first meaningful piece
            extracted = _normalize_query(item)
            if extracted:
                return extracted
        return ""
    try:
        return str(val).strip().lower()
    except Exception:  # noqa: BLE001
        return ""


def analyze_intent(state: RAGState) -> RAGState:
    raw_q = state.get("query", "")
    q = _normalize_query(raw_q)
    keywords = ("what", "how", "explain", "retrieval", "langgraph", "stream")
    needs = any(kw in q for kw in keywords)
    state["needs_retrieval"] = needs
    # Also store normalized form for downstream nodes if different
    if isinstance(raw_q, (dict, list)):
        state["query"] = q
    return state


def retrieve_if_needed(state: RAGState) -> RAGState:
    if state.get("needs_retrieval"):
        state["retrieved"] = retrieve_docs(state.get("query", ""))
    return state


def generate_answer(state: RAGState) -> RAGState:
    query = state.get("query", "")
    retrieved = state.get("retrieved", [])

    model_name = DEPLOYMENT or DEFAULT_MODEL

    def synthesize_answer() -> tuple[str, List[str]]:
        if not retrieved:
            text = f"Answer: {query}" if query else "No question provided."
            return text, [text]
        doc_summaries = "; ".join(r["text"] for r in retrieved)
        answer = f"Based on docs: {doc_summaries}\n\nAnswer: {query}"[:4000]
        return answer, [answer]

    if API_KEY and BASE_URL:
        client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
        try:
            resp = client.responses.create(model=model_name, input=query)
            text = getattr(resp, "output_text", None)
            if not text:
                text = json.dumps(resp.model_dump(mode="json", exclude_none=True))[:500]
            state["final_answer"] = text
            state["answer_parts"] = [text]
            return state
        except OpenAIError:  # fallback
            state["final_answer"], state["answer_parts"] = synthesize_answer()
            return state
    state["final_answer"], state["answer_parts"] = synthesize_answer()
    return state


# ---------------------------------------------------------------------------
# Build the LangGraph
# ---------------------------------------------------------------------------


def _build_graph():
    graph = StateGraph(RAGState)
    graph.add_node("analyze", analyze_intent)
    graph.add_node("retrieve", retrieve_if_needed)
    graph.add_node("answer", generate_answer)

    graph.add_edge(START, "analyze")
    graph.add_edge("analyze", "retrieve")
    graph.add_edge("retrieve", "answer")
    graph.add_edge("answer", END)
    return graph.compile()


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    graph = _build_graph()

    converter = RAGStateConverter(graph=graph)
    from_langgraph(graph, converter=converter).run()
