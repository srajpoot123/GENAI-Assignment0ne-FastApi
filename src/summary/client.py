from __future__ import annotations

import logging
from typing import TypedDict

from fastapi import HTTPException, status
from langchain_anthropic import ChatAnthropic
from langgraph.graph import END, START, StateGraph

from src.config import settings


logger = logging.getLogger("fastapi_assignment")


class SummaryState(TypedDict):
    text: str
    summary: str


def _build_llm() -> ChatAnthropic:
    api_key = settings.anthropic_api_key.strip()
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Anthropic API key is not configured",
        )

    return ChatAnthropic(
        model=settings.anthropic_model,
        api_key=api_key,
    )


def summarize_node(state: SummaryState) -> SummaryState:
    llm = _build_llm()
    prompt = (
        "You are a concise and professional summarizer. Summarize the following text in a clear, natural, and compact way. "
        "Keep the result informative but not too long.\n\n"
        f"Text: {state['text']}"
    )

    response = llm.invoke(prompt)
    content = getattr(response, "content", "")

    if isinstance(content, list):
        text_parts = []
        for item in content:
            if isinstance(item, str):
                text_parts.append(item)
            elif isinstance(item, dict):
                if item.get("type") == "text":
                    text_parts.append(str(item.get("text", "")))
            elif hasattr(item, "text"):
                text_parts.append(str(item.text))
        content = "".join(text_parts)

    summary = str(content).strip() if content is not None else ""
    if not summary:
        raise ValueError("Summary generation returned empty output")

    return {"text": state["text"], "summary": summary}


def build_summary_graph():
    graph = StateGraph(SummaryState)
    graph.add_node("summarize", summarize_node)
    graph.add_edge(START, "summarize")
    graph.add_edge("summarize", END)
    return graph.compile()


summary_graph = build_summary_graph()


def generate_summary(text: str) -> str:
    cleaned = text.strip()
    if not cleaned:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Text cannot be empty"
        )
    if len(cleaned) > settings.max_summary_text_length:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Text length exceeds the maximum of {settings.max_summary_text_length} characters",
        )

    try:
        result = summary_graph.invoke({"text": cleaned})
        summary_text = str(result.get("summary", "")).strip()
        if not summary_text:
            raise ValueError("Summary generation returned empty output")
        return summary_text
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("LangGraph/Anthropic summary invocation failed")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="LLM summarization failed or the Anthropic API is unavailable",
        ) from exc
