from utils.links import STATIC_LINKS
import os
from dotenv import load_dotenv
load_dotenv()


def post_process(state: dict) -> dict:
    print("[Post Process] Cleaning up...")
    print(f"[Post Process] Raw skills from Jason: {state['extracted'].get('skills', 'MISSING')}")

    extracted = state["extracted"].copy()

    def clean(text, is_date=False):
        if not text:
            return text
        if isinstance(text, list):
            text = ", ".join(text)
        text = str(text)
        text = text.replace("\u2014", ",")
        if is_date:
            text = text.replace("\u2013", "to")
        else:
            text = text.replace("\u2013", ",")
        return text

    extracted["name"] = clean(extracted.get("name", ""))
    extracted["title"] = clean(extracted.get("title", "")).replace(" , ", " | ")
    extracted["summary"] = clean(extracted.get("summary", ""))

    for exp in extracted.get("experience", []):
        exp["title"] = clean(exp.get("title", ""))
        exp["dates"] = clean(exp.get("dates", ""), is_date=True)
        exp["location"] = clean(exp.get("location", ""))
        bullets = exp.get("bullets", [])
        if isinstance(bullets, str):
            bullets = [bullets]
        exp["bullets"] = [clean(b) for b in bullets]

    for ed in extracted.get("education", []):
        ed["degree"] = clean(ed.get("degree", ""))
        ed["dates"] = clean(ed.get("dates", ""), is_date=True)
        ed["degree"] = ed["degree"].replace("B.Tech", "BE").replace("BTech", "BE")
        if "thapar" in ed.get("institution", "").lower():
            ed["institution"] = "Thapar Institute of Engineering and Technology"

    for proj in extracted.get("projects", []):
        desc = proj.get("description", "")
        if isinstance(desc, list):
            desc = " ".join(desc)
        proj["description"] = clean(desc)
        name = proj.get("name", "")
        for key, url in STATIC_LINKS["project_links"].items():
            if key.lower() in name.lower() or name.lower() in key.lower():
                proj["github"] = url
                break

    # Clean and normalise skill keys (Groq returns camelCase)
    # Clean and normalise skill keys (Groq returns camelCase)
    skills = extracted.get("skills", {})
    normalised_skills = {
        "technical": skills.get("technical") or skills.get("technicalSkills") or "",
        "tools": skills.get("tools") or skills.get("toolsAndPlatforms") or "",
        "languages": skills.get("languages") or skills.get("programmingLanguagesAndLibraries") or skills.get("programmingLanguages") or "",
        "certifications": skills.get("certifications") or ""
    }

    for key in normalised_skills:
        value = normalised_skills[key]
        if isinstance(value, list):
            value = ", ".join(value)
        normalised_skills[key] = clean(value)

    extracted["skills"] = normalised_skills

    extracted["linkedin"] = STATIC_LINKS["linkedin"]
    extracted["github"] = STATIC_LINKS["github"]
    extracted["portfolio"] = STATIC_LINKS["portfolio"]

    print(f"[Post Process] Skills after cleaning: {extracted.get('skills', 'MISSING')}")

    return {
        **state,
        "extracted": extracted,
        "messages": state["messages"] + [{
            "agent": "post_process",
            "action": "cleaned JSON",
            "note": "em dashes to comma, en dashes to to in dates only, fixed degree labels, injected static links, fixed Thapar full name"
        }]
    }