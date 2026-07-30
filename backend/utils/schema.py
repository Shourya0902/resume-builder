SCHEMA = {
    "type": "object",
    "required": ["name", "title", "location", "phone", "email", "summary", "experience", "education", "skills", "projects"],
    "properties": {
        "name": {"type": "string"},
        "title": {"type": "string"},
        "location": {"type": "string"},
        "phone": {"type": "string"},
        "email": {"type": "string"},
        "linkedin": {"type": "string"},
        "github": {"type": "string"},
        "portfolio": {"type": "string"},
        "summary": {"type": "string"},
        "experience": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["title", "company", "dates", "location", "bullets"],
                "properties": {
                    "title": {"type": "string"},
                    "company": {"type": "string"},
                    "dates": {"type": "string"},
                    "location": {"type": "string"},
                    "bullets": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                }
            }
        },
        "education": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["degree", "institution", "dates"],
                "properties": {
                    "degree": {"type": "string"},
                    "institution": {"type": "string"},
                    "dates": {"type": "string"}
                }
            }
        },
        "projects": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["name", "tools", "description"],
                "properties": {
                    "name": {"type": "string"},
                    "tools": {"type": "string"},
                    "github": {"type": "string"},
                    "description": {"type": "string"}
                }
            }
        },
        "skills": {
            "type": "object",
            "required": ["technical", "tools", "languages", "certifications"],
            "properties": {
                "technical": {"type": "string"},
                "tools": {"type": "string"},
                "languages": {"type": "string"},
                "certifications": {"type": "string"}
            }
        }
    }
}