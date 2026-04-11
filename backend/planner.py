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
    Extract JSON safely from LLM response
    """
    try:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        return json.loads(match.group())
    except Exception:
        return {
            "steps": ["Search for relevant information", "Extract insights"],
            "tools": ["search", "scraper"]
        }


def create_plan(query: str):
    """
    Generate a plan using Gemini
    """

    prompt = f"""
You are an AI planner.

Break the user query into clear steps and decide which tools are required.

Available tools:
- search: find relevant links
- scraper: extract content from URLs

Rules:
- Be concise
- Only include necessary steps
- ALWAYS return valid JSON
- Do not include any explanation

Output format:
{{
  "steps": ["...", "..."],
  "tools": ["search", "scraper"]
}}

User Query:
{query}
"""

    try:
        response = model.generate_content(prompt)

        content = response.text

        plan = extract_json(content)

        # basic validation
        if "steps" not in plan or "tools" not in plan:
            raise ValueError("Invalid plan format")

        return plan

    except Exception as e:
        print(f"[PLANNER ERROR]: {e}")

        return {
            "steps": [
                "Search for relevant information",
                "Extract and summarize key points"
            ],
            "tools": ["search", "scraper"]
        }