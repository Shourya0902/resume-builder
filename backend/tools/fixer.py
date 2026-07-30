import json
import ollama
from groq import Groq
from config import VALIDATION_MODEL, USE_GROQ
from utils.schema import SCHEMA
import os
from dotenv import load_dotenv
load_dotenv()

def get_client():
    if USE_GROQ:
        from config import GROQ_API_KEY
        return Groq(api_key=GROQ_API_KEY)
    else:
        return ollama.Client(host="http://localhost:11434")


def fixer(state: dict) -> dict:
    print("[Fixer] Fixing formatting issues...")

    prompt = f"""
ROLE: You are a precise JSON formatting fixer. You fix ONLY specific formatting issues in a JSON object. You do not change anything else.

TASK: Fix ONLY the formatting issues listed below in the JSON. Do not change any content, do not rewrite any bullets, do not touch anything that is not mentioned in the issues list.

FORMATTING ISSUES TO FIX:
{chr(10).join(state['formatting_issues'])}

RULES:
- Replace any em dashes or en dashes with a comma or rewrite naturally without them
- Date separators must use "to" for example "Feb 2022 to Jul 2024"
- Degree names must not contain any dashes
- Do not touch anything else in the JSON

JSON TO FIX:
{json.dumps(state['extracted'], indent=2)}

Return the corrected JSON only, nothing else.
"""

    if USE_GROQ:
        response = get_client().chat.completions.create(
            model=VALIDATION_MODEL,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0
        )
        fixed = json.loads(response.choices[0].message.content)
    else:
        response = get_client().chat(
            model=VALIDATION_MODEL,
            messages=[{"role": "user", "content": prompt}],
            format=SCHEMA,
            options={"temperature": 0},
            think=False
        )
        fixed = json.loads(response.message.content)

    return {
        **state,
        "extracted": fixed,
        "formatting_issues": [],
        "messages": state["messages"] + [{
            "agent": "fixer",
            "action": "fixed formatting issues",
            "issues_fixed": state["formatting_issues"]
        }]
    }