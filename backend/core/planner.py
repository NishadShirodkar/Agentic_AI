import json
import os
import re

import google.generativeai as genai

from models.schemas import ExecutionPlan

DEFAULT_PLAN = ExecutionPlan(
    steps=[
        "Search for relevant sources",
        "Scrape and collect evidence",
        "Filter and rank the evidence",
    ],
    tools=["search", "scraper", "filter"],
)


def _extract_json(text: str) -> dict:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("Planner did not return JSON")
    return json.loads(match.group())


def create_plan(query: str) -> ExecutionPlan:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return DEFAULT_PLAN

    prompt = f"""
You are a planning component for a research agent.
Return only valid JSON with keys: steps, tools.
Allowed tools: search, scraper, filter.

Query: {query}
"""

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("models/gemini-2.5-flash")
        response = model.generate_content(prompt)
        payload = _extract_json(response.text)
        plan = ExecutionPlan(**payload)

        # Ensure execution can proceed even if model output is incomplete.
        if not plan.tools:
            plan.tools = ["search", "scraper", "filter"]
        if not plan.steps:
            plan.steps = DEFAULT_PLAN.steps

        return plan
    except Exception:
        return DEFAULT_PLAN
