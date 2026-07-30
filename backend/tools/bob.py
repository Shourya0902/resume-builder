import os
from dotenv import load_dotenv
load_dotenv()

from utils.template import build_doc


def bob(state: dict) -> dict:
    print("[Bob] Building Word document...")
    print(f"[Bob] Skills data: {state['extracted'].get('skills', 'MISSING')}")

    output_path = state["output_path"]
    
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    
    build_doc(state["extracted"], output_path=output_path)
    
    if os.path.exists(output_path):
        print(f"[Bob] Verified. File exists at {output_path}")
    else:
        print(f"[Bob] ERROR. File not found at {output_path}")

    return {
        **state,
        "output_path": output_path
    }