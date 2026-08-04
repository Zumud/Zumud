"""Deterministic OpenAI chat-completions stub for the e2e mocked-AI lane.

Serves the two endpoints ai_service uses (plain completions and structured
`parse`), picking a fixture by the requested json_schema name. Point the
backend at it with OPENAI_BASE_URL=http://127.0.0.1:9010/v1 — everything else
in the e2e stack (Supabase, backend, frontend, LaTeX compiler) stays real.
"""

import json
import time

from fastapi import FastAPI, Request

app = FastAPI()

STRUCTURED_RESUME = {
    "personal_info": {
        "name": "Jane Doe",
        "email": "jane.doe@example.com",
        "phone": "+49 30 1234567",
        "location": "Berlin, Germany",
        "linkedin": None,
        "github": None,
    },
    "summary": "Platform engineer with ten years of Python and cloud experience, "
    "focused on reliable delivery pipelines.",
    "skills": [
        {"category": "Languages", "items": ["Python", "TypeScript", "SQL"]},
        {"category": "Infrastructure", "items": ["Docker", "PostgreSQL", "Linux"]},
    ],
    "experience": [
        {
            "company": "Acme Corp",
            "role": "Senior Platform Engineer",
            "location": "Berlin",
            "date_range": "2019 - 2026",
            "description": None,
            "achievements": [
                "Cut infrastructure spend by forty percent",
                "Led a team of five engineers through a zero-downtime migration",
            ],
        }
    ],
    "education": [
        {
            "institution": "TU Berlin",
            "degree": "BSc Computer Science",
            "location": "Berlin",
            "date_range": "2012 - 2016",
            "minors": None,
        }
    ],
    "certifications": None,
    "projects": None,
    "publications": None,
    "awards": None,
}

# Keyed by the pydantic response_format model name the backend requests.
FIXTURES = {
    "StructuredResume": STRUCTURED_RESUME,
    "TailoredResume": {
        "tailored_resume": "Jane Doe\nSenior Platform Engineer\n"
        "Ten years of Python, tailored for this role."
    },
    "TailoredCoverLetter": {
        "tailored_coverletter": "Dear Hiring Team,\n\nI am excited to apply. "
        "My decade of Python experience matches your needs.\n\nJane Doe"
    },
    "TailoredAnswer": {
        "tailored_answer": "I bring ten years of directly relevant experience."
    },
    "CompanyName": {"company_name": "Acme Corp"},
}

PLAIN_TEXT = "Jane Doe\nSenior Platform Engineer\nTen years of Python experience."

# Standing in for the model when a .tex upload is being converted (templatizer.py).
# The templatizer accepts nothing it has not rendered against both reference resumes
# and compiled for real, so a stub returning prose would only ever exercise the
# failure path. This is a genuine Jinja body: plain LaTeX so it works under any
# uploaded preamble, and guarded throughout so `resume_minimal` — a name and one
# employer, every other field null — renders without a stranded heading or an empty
# list environment. tests/unit/test_e2e_ai_stub.py holds it to that.
TEMPLATIZED_BODY = r"""
\begin{center}
{\LARGE \textbf{ {{ personal_info.name }} }}
{% if personal_info.email %}\\ {{ personal_info.email }}{% endif %}
{% if personal_info.phone %}\\ {{ personal_info.phone }}{% endif %}
{% if personal_info.location %}\\ {{ personal_info.location }}{% endif %}
\end{center}

{% if summary %}{{ summary }}\par{% endif %}

{% if skills %}
\section*{Skills}
\begin{itemize}
{% for skill in skills %}\item \textbf{ {{ skill.category }} }: {{ skill['items']|join(', ') }}
{% endfor %}
\end{itemize}
{% endif %}

{% if experience %}
\section*{Experience}
{% for job in experience %}
\noindent \textbf{ {{ job.company }} }{% if job.role %} --- {{ job.role }}{% endif %}{% if job.date_range %} \hfill {{ job.date_range }}{% endif %}
\par
{% if job.description %}{{ job.description }}\par{% endif %}
{% if job.achievements %}
\begin{itemize}
{% for achievement in job.achievements %}\item {{ achievement }}
{% endfor %}
\end{itemize}
{% endif %}
{% endfor %}
{% endif %}

{% if education %}
\section*{Education}
\begin{itemize}
{% for entry in education %}\item \textbf{ {{ entry.institution }} }{% if entry.degree %} --- {{ entry.degree }}{% endif %}{% if entry.date_range %} \hfill {{ entry.date_range }}{% endif %}
{% endfor %}
\end{itemize}
{% endif %}
"""


def _is_templatization(body: dict) -> bool:
    """Whether this is the templatizer asking, rather than the tailoring service.

    Both send plain completions with no json_schema to pick a fixture by, so the one
    thing that distinguishes them is what they ask for. Keyed on the templatizer's
    system prompt (backend/core/templatizer.py).
    """
    return any(
        message.get("role") == "system" and "Jinja2" in (message.get("content") or "")
        for message in body.get("messages") or []
    )


@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    body = await request.json()
    schema_name = ((body.get("response_format") or {}).get("json_schema") or {}).get(
        "name"
    )
    if schema_name:
        content = json.dumps(FIXTURES[schema_name])
    elif _is_templatization(body):
        content = TEMPLATIZED_BODY
    else:
        content = PLAIN_TEXT

    return {
        "id": "chatcmpl-e2e-stub",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": body.get("model", "stub"),
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": content},
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
    }
