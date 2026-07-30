import os
from typing import TypedDict, List, Dict
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv

load_dotenv()

from tools.jason import jason
from tools.post_process import post_process
from tools.valley import valley
from tools.fixer import fixer
from tools.resolver import resolver
from tools.bob import bob
from config import OUTPUT_DIR
from utils.template import convert_to_pdf

app = FastAPI()

class CVState(TypedDict):
    original_text: str
    extracted: dict
    content_issues: List[str]
    formatting_issues: List[str]
    retry_count: int
    output_path: str
    messages: List[Dict]

def should_retry(state: CVState) -> str:
    content_issues = state.get("content_issues", [])
    formatting_issues = state.get("formatting_issues", [])

    if not content_issues and not formatting_issues:
        print("[Router] All clean, building doc...")
        return "build"
    elif state["retry_count"] >= 3:
        print("[Router] Max attempts reached, building doc anyway...")
        return "build"
    elif formatting_issues and not content_issues:
        print("[Router] Formatting issues only, sending to Fixer...")
        return "fix"
    elif content_issues and not formatting_issues:
        print("[Router] Content issues only, sending to Resolver...")
        return "resolve"
    else:
        print("[Router] Both issues, sending to Fixer first...")
        return "fix"

def build_graph():
    graph = StateGraph(CVState)
    graph.add_node("jason", jason)
    graph.add_node("post_process", post_process)
    graph.add_node("valley", valley)
    graph.add_node("fixer", fixer)
    graph.add_node("resolver", resolver)
    graph.add_node("bob", bob)
    graph.set_entry_point("jason")
    graph.add_edge("jason", "post_process")
    graph.add_edge("post_process", "valley")
    graph.add_conditional_edges(
        "valley",
        should_retry,
        {"build": "bob", "fix": "fixer", "resolve": "resolver"}
    )
    graph.add_edge("fixer", "valley")
    graph.add_edge("resolver", "valley")
    graph.add_edge("bob", END)
    return graph.compile()

pipeline = build_graph()

class CVRequest(BaseModel):
    cv_text: str

def run_pipeline(cv_text: str) -> str:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    abs_output_dir = os.path.join(base_dir, OUTPUT_DIR)
    os.makedirs(abs_output_dir, exist_ok=True)
    output_path = os.path.join(abs_output_dir, "CV_output.docx")

    initial_state = CVState(
        original_text=cv_text,
        extracted={},
        content_issues=[],
        formatting_issues=[],
        retry_count=0,
        output_path=output_path,
        messages=[]
    )

    result = pipeline.invoke(initial_state)
    return result["output_path"]

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/generate")
def generate(request: CVRequest):
    if not request.cv_text.strip():
        raise HTTPException(status_code=400, detail="CV text cannot be empty")
    try:
        docx_path = run_pipeline(request.cv_text)
        if not os.path.exists(docx_path):
            raise HTTPException(status_code=500, detail="CV generation failed, file not found")
        with open(docx_path, "rb") as f:
            content = f.read()
        return Response(
            content=content,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": "attachment; filename=CV_output.docx"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate/pdf")
def generate_pdf(request: CVRequest):
    if not request.cv_text.strip():
        raise HTTPException(status_code=400, detail="CV text cannot be empty")
    try:
        docx_path = run_pipeline(request.cv_text)
        if not os.path.exists(docx_path):
            raise HTTPException(status_code=500, detail="CV generation failed, file not found")
        pdf_path = convert_to_pdf(docx_path)
        if not pdf_path:
            raise HTTPException(status_code=500, detail="PDF conversion failed")
        with open(pdf_path, "rb") as f:
            content = f.read()
        return Response(
            content=content,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=CV_output.pdf"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))