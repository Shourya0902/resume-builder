import json
import ollama
from groq import Groq
from config import EXTRACTION_MODEL, USE_GROQ
from utils.links import STATIC_LINKS
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


def jason(state: dict) -> dict:
    print(f"[Jason] Extracting CV... (attempt {state['retry_count'] + 1})")

    feedback = ""
    if state["content_issues"]:
        feedback = f"""
PREVIOUS EXTRACTION HAD THESE CONTENT ISSUES, FIX THEM:
{chr(10).join(state['content_issues'])}
"""

    prompt = f"""
ROLE: You are an expert CV parser that extracts structured information from resume text with perfect accuracy.

TASK: Extract all information from the CV text below into structured JSON. Do not summarise, paraphrase, or change any wording except where formatting rules below require it.

CONTEXT: This is a professional CV for a data science role. It contains sections for contact details, summary, work experience, projects, education, and skills. All dates, metrics, bullet points, certifications and education entries must be preserved exactly as written.

FORMAT RULES:
- Preserve all dates for every experience and education entry
- Keep experience entries in the exact order they appear in the CV
- Keep all bullet points exactly as written, do not merge or shorten them
- Include certifications inside the skills section
- Extract every education entry including degree name, institution and dates
- LinkedIn, GitHub and Portfolio should be labelled as such, not as URLs
- All date ranges must use "to" as the separator, for example "Feb 2022 to Jul 2024"
- Remove all em dashes and en dashes from all text fields and replace with a comma or rewrite naturally
- In degree names do not use any dashes, write "MSc Data Science and Analytics, Distinction" not "MSc Data Science and Analytics — Distinction"

{feedback}

CV TEXT:
{state['original_text']}
"""

    if USE_GROQ:
        response = get_client().chat.completions.create(
            model=EXTRACTION_MODEL,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0
        )
        extracted = json.loads(response.choices[0].message.content)
    else:
        response = get_client().chat(
            model=EXTRACTION_MODEL,
            messages=[{"role": "user", "content": prompt}],
            format=SCHEMA,
            options={"temperature": 0},
            think=False
        )
        extracted = json.loads(response.message.content)

    return {
        **state,
        "extracted": extracted,
        "content_issues": [],
        "formatting_issues": [],
        "retry_count": state["retry_count"] + 1,
        "messages": state["messages"] + [{
            "agent": "jason",
            "attempt": state["retry_count"] + 1,
            "action": "extracted CV into JSON",
            "note": "applied formatting rules: em dashes removed, dates use to, B.Tech changed to BE"
        }]
    }