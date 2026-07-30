import streamlit as st
import requests
import subprocess
import tempfile
import os

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="CV Generator", page_icon="📄")
st.title("CV Generator")

# Initialize session state
if "docx_bytes" not in st.session_state:
    st.session_state["docx_bytes"] = None
if "pdf_bytes" not in st.session_state:
    st.session_state["pdf_bytes"] = None
if "latex_pdf_bytes" not in st.session_state:
    st.session_state["latex_pdf_bytes"] = None

tab1, tab2 = st.tabs(["CV Generator", "LaTeX to PDF"])

# ── TAB 1
with tab1:
    cv_text = st.text_area("Paste your CV text here", height=400)

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Generate Word", type="primary", use_container_width=True):
            if not cv_text.strip():
                st.error("Please paste your CV text first.")
            else:
                with st.spinner("Generating..."):
                    try:
                        response = requests.post(
                            f"{API_URL}/generate",
                            json={"cv_text": cv_text},
                            timeout=300
                        )
                        if response.status_code == 200:
                            st.session_state["docx_bytes"] = response.content
                            st.session_state["pdf_bytes"] = None
                            st.success("Done!")
                        else:
                            st.error(f"Error: {response.text}")
                    except Exception as e:
                        st.error(f"Something went wrong: {str(e)}")

    with col2:
        if st.button("Generate PDF", type="secondary", use_container_width=True):
            if not cv_text.strip():
                st.error("Please paste your CV text first.")
            else:
                with st.spinner("Generating and converting..."):
                    try:
                        response = requests.post(
                            f"{API_URL}/generate/pdf",
                            json={"cv_text": cv_text},
                            timeout=300
                        )
                        if response.status_code == 200:
                            st.session_state["pdf_bytes"] = response.content
                            st.session_state["docx_bytes"] = None
                            st.success("Done!")
                        else:
                            st.error(f"Error: {response.text}")
                    except Exception as e:
                        st.error(f"Something went wrong: {str(e)}")

    if st.session_state["docx_bytes"]:
        st.download_button(
            label="Download CV.docx",
            data=st.session_state["docx_bytes"],
            file_name="CV_output.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True
        )

    if st.session_state["pdf_bytes"]:
        st.download_button(
            label="Download CV.pdf",
            data=st.session_state["pdf_bytes"],
            file_name="CV_output.pdf",
            mime="application/pdf",
            use_container_width=True
        )

# ── TAB 2
with tab2:
    latex_code = st.text_area(
        "Paste your LaTeX code here",
        height=400,
        placeholder="\\documentclass{article}\n\\begin{document}\nHello World\n\\end{document}"
    )

    if st.button("Compile to PDF", type="primary"):
        if not latex_code.strip():
            st.error("Please paste your LaTeX code first.")
        else:
            with st.spinner("Compiling..."):
                try:
                    # Replace outdated packages
                    latex_code = latex_code.replace(
                        r'\usepackage{fullpage}',
                        r'\usepackage[top=0.5in,bottom=0.5in,left=0.75in,right=0.75in]{geometry}'
                    )

                    with tempfile.TemporaryDirectory() as tmpdir:
                        tex_path = os.path.join(tmpdir, "document.tex")
                        pdf_path = os.path.join(tmpdir, "document.pdf")

                        with open(tex_path, "w", encoding="utf-8") as f:
                            f.write(latex_code)

                        result = subprocess.run(
                            [
                                "pdflatex",
                                "-interaction=nonstopmode",
                                "-output-directory", tmpdir,
                                tex_path
                            ],
                            capture_output=True,
                            text=True,
                            timeout=60
                        )

                        if os.path.exists(pdf_path):
                            with open(pdf_path, "rb") as f:
                                st.session_state["latex_pdf_bytes"] = f.read()
                            st.success("Compiled successfully!")
                        else:
                            st.session_state["latex_pdf_bytes"] = None
                            st.error("Compilation failed. Check your LaTeX code.")
                            with st.expander("Error log"):
                                st.code(result.stdout + result.stderr)

                except subprocess.TimeoutExpired:
                    st.error("Compilation timed out.")
                except FileNotFoundError:
                    st.error("pdflatex not found.")
                except Exception as e:
                    st.error(f"Something went wrong: {str(e)}")

    if st.session_state["latex_pdf_bytes"]:
        st.download_button(
            label="Download PDF",
            data=st.session_state["latex_pdf_bytes"],
            file_name="document.pdf",
            mime="application/pdf",
            use_container_width=True
        )