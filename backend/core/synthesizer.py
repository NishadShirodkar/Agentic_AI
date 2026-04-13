import json
import os
import re

import google.generativeai as genai

from models.schemas import ResearchResult, SourceEvidence


def _extract_json(text: str) -> dict:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("Synthesizer did not return JSON")
    return json.loads(match.group())


def _default_result(query: str, sources: list[SourceEvidence], message: str) -> ResearchResult:
    return ResearchResult(
        question=query,
        short_answer=message,
        key_findings=[],
        sources=[SourceEvidence(url=s.url, snippet=s.snippet, content="") for s in sources[:3]],
        confidence="Low",
        limitations=["Model generation failed"],
        next_steps=["Retry the request", "Try a more specific query"],
    )


def _sanitize_sources(returned_sources: list[dict], stored_sources: list[SourceEvidence]) -> list[SourceEvidence]:
    allowed = {s.url: s for s in stored_sources}
    cleaned: list[SourceEvidence] = []

    for item in returned_sources:
        url = item.get("url", "")
        if url not in allowed:
            continue
        snippet = item.get("snippet") or allowed[url].snippet
        cleaned.append(SourceEvidence(url=url, snippet=snippet[:240], content=""))

    if cleaned:
        return cleaned

    return [SourceEvidence(url=s.url, snippet=s.snippet, content="") for s in stored_sources[:3]]


def synthesize(query: str, sources: list[SourceEvidence]) -> ResearchResult:
    if not sources:
        return ResearchResult(
            question=query,
            short_answer="Insufficient data to answer the question.",
            key_findings=[],
            sources=[],
            confidence="Low",
            limitations=["No reliable sources found"],
            next_steps=["Refine the query", "Try broader search terms"],
        )

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return _default_result(query, sources, "Model key is missing; synthesis could not run.")

    context = "\n\n".join(
        f"URL: {s.url}\nSnippet: {s.snippet}\nContent: {s.content[:1200]}"
        for s in sources
    )

    prompt = f"""
You are the synthesizer for a research agent.
Use only the supplied source context.
Return only valid JSON with this schema:
{{
  "question": "...",
  "short_answer": "...",
  "key_findings": ["..."],
  "sources": [{{"url": "...", "snippet": "..."}}],
  "confidence": "High|Medium|Low",
  "limitations": ["..."],
  "next_steps": ["..."]
}}

Do not cite any source URL that is not present in the provided context.

Question: {query}
Context:\n{context}
"""

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("models/gemini-2.5-flash")
        response = model.generate_content(prompt)
        payload = _extract_json(response.text)

        result = ResearchResult(**payload)
        result.sources = _sanitize_sources(payload.get("sources", []), sources)
        return result
    except Exception:
        return _default_result(query, sources, "Error generating structured answer.")
