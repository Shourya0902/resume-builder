import json
import ollama
from groq import Groq
from config import VALIDATION_MODEL, USE_GROQ
import os
from dotenv import load_dotenv
load_dotenv()

def get_client():
    if USE_GROQ:
        from config import GROQ_API_KEY
        return Groq(api_key=GROQ_API_KEY)
    else:
        return ollama.Client(host="http://localhost:11434")

VALIDATION_SCHEMA = {
    "type": "object",
    "properties": {
        "content_issues": {"type": "array", "items": {"type": "string"}},
        "formatting_issues": {"type": "array", "items": {"type": "string"}},
        "verdict": {"type": "string"}
    },
    "required": ["content_issues", "formatting_issues", "verdict"]
}


def valley(state: dict) -> dict:
    print("[Valley] Validating extracted CV...")

    prompt = f"""
ROLE: You are a strict CV validation agent with full context of what every agent in this pipeline has done.

TASK: Compare the extracted JSON against the original CV text and find genuine issues. Use the agent message log to understand what changes were intentional.

AGENT MESSAGE LOG - THESE ARE INTENTIONAL CHANGES, DO NOT FLAG THEM:
{json.dumps(state['messages'], indent=2)}

WHAT TO FLAG AS CONTENT ISSUES:
- A bullet point is missing or its meaning was changed
- A metric was dropped or altered
- An experience or education entry is missing
- Experience is in the wrong order
- Any real information from the original CV is absent from the JSON

WHAT TO FLAG AS FORMATTING ISSUES:
- Em dashes or en dashes still present despite post_process running
- Date separator is not "to" despite post_process running
- Any formatting rule from the agent log that was not applied correctly

WHAT NOT TO FLAG:
- Changes explicitly listed in the agent message log as intentional
- Information that exists anywhere in the JSON even if in a different section
- Things that could be clearer or more explicit but are not wrong
- When in doubt, do not flag it

STRICT RULES:
- Only flag information that is completely absent from the JSON
- Do not flag things that appear in a different section than expected
- Do not flag missing context or interpretation issues
- If the information exists anywhere in the JSON it is not a content issue

ORIGINAL CV TEXT:
{state['original_text']}

EXTRACTED JSON:
{json.dumps(state['extracted'], indent=2)}

Respond in this exact JSON format:
{{
    "content_issues": ["issue 1", "issue 2"],
    "formatting_issues": ["issue 1", "issue 2"],
    "verdict": "clean or issues"
}}

If there are no genuine issues return empty lists and verdict as clean.
"""

    if USE_GROQ:
        response = get_client().chat.completions.create(
            model=VALIDATION_MODEL,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0
        )
        result = json.loads(response.choices[0].message.content)
    else:
        response = get_client().chat(
            model=VALIDATION_MODEL,
            messages=[{"role": "user", "content": prompt}],
            format=VALIDATION_SCHEMA,
            options={"temperature": 0},
            think=False
        )
        result = json.loads(response.message.content)

    print(f"[Valley] Verdict: {result['verdict']}")
    if result["content_issues"]:
        print(f"[Valley] Content issues: {result['content_issues']}")
    if result["formatting_issues"]:
        print(f"[Valley] Formatting issues: {result['formatting_issues']}")

    return {
        **state,
        "content_issues": result["content_issues"],
        "formatting_issues": result["formatting_issues"]
    }