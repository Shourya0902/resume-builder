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


def resolver(state: dict) -> dict:
    print("[Resolver] Fixing content issues surgically...")

    prompt = f"""
ROLE: You are a precise CV content fixer. You fix ONLY specific content issues in a JSON object by referring back to the original CV text. You do not change anything else.

TASK: Fix ONLY the content issues listed below. Look at the original CV text to find the correct information and update only those specific fields in the JSON. Do not touch anything that is not mentioned in the issues list.

CONTENT ISSUES TO FIX:
{chr(10).join(state['content_issues'])}

IMPORTANT CONTEXT - THESE ARE INTENTIONAL CHANGES ALREADY MADE, DO NOT REVERT THEM:
{json.dumps(state['messages'], indent=2)}

RULES:
- Only fix what is listed in the content issues above
- Refer to the original CV text to get the correct information
- Do not change any formatting, do not revert intentional changes
- Do not touch bullets, metrics or fields not mentioned in the issues
- Return the complete corrected JSON

ORIGINAL CV TEXT:
{state['original_text']}

CURRENT JSON:
{json.dumps(state['extracted'], indent=2)}
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
        "content_issues": [],
        "messages": state["messages"] + [{
            "agent": "resolver",
            "action": "fixed content issues",
            "issues_fixed": state["content_issues"]
        }]
    }