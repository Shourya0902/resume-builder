# CV Generation Agent

An agentic AI pipeline that takes raw CV text and generates a professionally formatted Word document and PDF. Built with LangGraph, FastAPI, Streamlit, and local LLMs via Ollama or Groq.

## What it does

Paste your CV text (generated from Claude or any source) and the pipeline:

1. **Jason** extracts all CV content into structured JSON
2. **Post Process** cleans formatting, injects static links, normalises fields
3. **Valley** validates the extracted JSON against the original text
4. **Fixer** surgically fixes formatting issues (em dashes, date separators)
5. **Resolver** surgically fixes content issues (missing bullets, wrong order)
6. **Bob** builds a clean, ATS-friendly Word document

Download as `.docx` or `.pdf`. Also includes a standalone LaTeX to PDF compiler.

## Stack

- **LangGraph** - agentic pipeline orchestration
- **FastAPI** - backend API
- **Streamlit** - frontend UI
- **Ollama** - local LLM inference (default: qwen3:latest)
- **Groq** - cloud LLM inference (llama-3.1-8b-instant + llama-3.3-70b-versatile)
- **python-docx** - Word document generation
- **LibreOffice** - Word to PDF conversion
- **pdflatex** - LaTeX to PDF compilation

## Project Structure

```
resume-builder/
├── backend/
│   ├── main.py              # FastAPI + LangGraph graph wiring
│   ├── config.py            # Model config, environment variables
│   ├── tools/
│   │   ├── jason.py         # CV extraction agent
│   │   ├── post_process.py  # Cleaning and normalisation
│   │   ├── valley.py        # Validation agent
│   │   ├── fixer.py         # Formatting fixer agent
│   │   ├── resolver.py      # Content fixer agent
│   │   └── bob.py           # Word document builder
│   └── utils/
│       ├── template.py      # python-docx Word template
│       ├── schema.py        # JSON extraction schema
│       └── links.py         # Static links (LinkedIn, GitHub, etc.)
├── frontend/
│   └── app.py               # Streamlit UI
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── run.sh                   # Local dev startup script
```

## Agent Flow

```
CV Text Input
    │
    ▼
Jason (extraction)
    │
    ▼
Post Process (cleaning)
    │
    ▼
Valley (validation)
    │
    ├── clean ──────────────────── Bob (build doc) ── Output
    │
    ├── formatting issues ──────── Fixer ── Valley
    │
    └── content issues ─────────── Resolver ── Valley
```

## Setup

### Local (Ollama)

**1. Install Ollama**

Download from [ollama.com](https://ollama.com) then pull the model:

```bash
ollama pull qwen3:latest
```

**2. Install dependencies**

```bash
git clone https://github.com/Shourya0902/resume-builder.git
cd resume-builder
uv venv
source .venv/bin/activate
uv add fastapi uvicorn streamlit langgraph langchain-core python-docx groq ollama requests pydantic python-dotenv
```

**3. Install LibreOffice and pdflatex (for PDF export)**

```bash
brew install --cask libreoffice
brew install --cask basictex
sudo tlmgr install titlesec enumitem geometry
```

**4. Configure environment**

Create a `.env` file in the project root:

```bash
USE_GROQ=false
OLLAMA_HOST=http://localhost:11434
EXTRACTION_MODEL=qwen3:latest
VALIDATION_MODEL=qwen3:latest
OUTPUT_DIR=outputs
API_URL=http://localhost:8000
```

**5. Run**

```bash
chmod +x run.sh
./run.sh
```

Open `http://localhost:8501` in your browser.

### Cloud (Groq)

Get a free API key from [console.groq.com](https://console.groq.com/keys) then update `.env`:

```bash
USE_GROQ=true
GROQ_API_KEY=your_key_here
OUTPUT_DIR=outputs
API_URL=http://localhost:8000
```

### Docker

```bash
docker compose up --build
```

Open `http://localhost:8501`.

## Usage

**Tab 1: CV Generator**
1. Paste your CV text
2. Click Generate Word or Generate PDF
3. Download your formatted CV

**Tab 2: LaTeX to PDF**
1. Paste your LaTeX CV code
2. Click Compile to PDF
3. Download the PDF

## Switching between Ollama and Groq

In `.env` set:

```bash
USE_GROQ=false   # use local Ollama
USE_GROQ=true    # use Groq cloud API
```

Restart the server after changing.

## Roadmap

- [ ] Job description fetching via Indeed API
- [ ] CV tailoring to specific job descriptions
- [ ] Multiple CV template styles
- [ ] User profile form for dynamic static links
- [ ] Adzuna job search integration
- [ ] Full agentic job application pipeline

## Author

Shourya Marwaha - [LinkedIn](https://www.linkedin.com/in/shouryamarwaha/) | [GitHub](https://github.com/Shourya0902) | [Portfolio](https://shouryam-portfolio.framer.website/)
