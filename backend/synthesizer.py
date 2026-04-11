import google.generativeai as genai
import json
import re
import os
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("models/gemini-2.5-flash")


def extract_json(text: str):
    """
    Safely extract JSON from LLM response
    """
    try:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        return json.loads(match.group())
    except Exception:
        return None


def synthesize(query: str, data: list):
    """
    Generate final structured answer using Gemini
    """

    print("\n[SYNTHESIZER] Generating final answer...")

    # -------------------------
    # Handle empty data case
    # -------------------------
    if not data:
        return {
            "question": query,
            "short_answer": "Insufficient data to answer the question.",
            "key_findings": [],
            "sources": [],
            "confidence": "Low",
            "limitations": ["No reliable sources found"],
            "next_steps": ["Try refining the query"]
        }

    # -------------------------
    # Prepare context
    # -------------------------
    context = "\n\n".join([
        f"Source: {d['url']}\nContent: {d['content'][:1000]}"
        for d in data
    ])

    # -------------------------
    # Prompt
    # -------------------------
    prompt = f"""
You are an expert AI research analyst.

Use the provided context to answer the question.

IMPORTANT:
- Prefer widely used RAG databases such as Chroma, Weaviate, Milvus, and Qdrant when relevant.
- You are allowed to synthesize and infer insights from the context.
- Even if direct comparison is not given, derive a reasonable comparison.
- Do NOT say "information is insufficient" unless absolutely necessary.
- Be confident but do NOT hallucinate facts not supported by context.

CRITICAL RULES:
- key_findings MUST be a list of plain text sentences (strings)
- DO NOT return objects or nested JSON inside key_findings
- Each finding must be clear, specific, and informative

FOR COMPARISON QUESTIONS:
- Always produce a clear comparison
- Assign each entity a strength (e.g., best for scalability, best for ease of use, best for performance)

FOR ENTITY / COMPANY QUESTIONS:
- For each company:
  - Clearly explain what they do
  - Mention their target customer (SME, enterprise, etc.)
  - Highlight what makes them unique or different
- Avoid generic statements like "is an HR SaaS startup"

Output ONLY valid JSON.

Format:
{{
  "question": "...",
  "short_answer": "...",
  "key_findings": ["Sentence 1", "Sentence 2"],
  "sources": ["...", "..."],
  "confidence": "High/Medium/Low",
  "limitations": ["..."],
  "next_steps": ["..."]
}}

Question:
{query}

Context:
{context}
"""

    try:
        response = model.generate_content(prompt)

        content = response.text

        result = extract_json(content)

        if not result:
            raise ValueError("Invalid JSON output")

        return result

    except Exception as e:
        print(f"[SYNTHESIZER ERROR]: {e}")

        return {
            "question": query,
            "short_answer": "Error generating structured answer.",
            "key_findings": [],
            "sources": [d["url"] for d in data],
            "confidence": "Low",
            "limitations": ["LLM output parsing failed"],
            "next_steps": ["Retry or improve prompt"]
        }