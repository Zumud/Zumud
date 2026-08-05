"""Model answers to a templatization request, shared by the unit and e2e lanes.

Kept in one place so that raising the bar in `verify()` cannot leave one lane passing
and the other broken. Both are plain LaTeX, so they work under whatever preamble the
uploaded document brought, and both are guarded throughout, so `resume_minimal` — a name
and one employer, every other field null — renders no stranded heading and no empty list
environment, which would be a compile error.

DESIGN_BODY is what the model realistically returns: a faithful conversion of the design
in front of it, which prints the two things that design showed and nothing else. It is
what the e2e stub answers with, so the lane covers the filling of the gaps
(`fill_missing_sections`) rather than assuming a model that never leaves any.

COMPLETE_BODY covers every section, and is the candidate the templatizer's unit tests
hand to `verify()` directly — the only kind it accepts.
"""

DESIGN_BODY = r"""
\begin{center}
{\LARGE \textbf{ {{ personal_info.name }} }}
{% if personal_info.email %}\\ {{ personal_info.email }}{% endif %}
\end{center}

{% if experience %}
\section*{Experience}
{% for job in experience %}
\noindent \textbf{ {{ job.company }} }{% if job.role %} --- {{ job.role }}{% endif %}{% if job.date_range %} \hfill {{ job.date_range }}{% endif %}
\par
{% if job.achievements %}
\begin{itemize}
{% for achievement in job.achievements %}\item {{ achievement }}
{% endfor %}
\end{itemize}
{% endif %}
{% endfor %}
{% endif %}
"""

COMPLETE_BODY = r"""
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

{% if projects %}
\section*{Projects}
{% for project in projects %}
\noindent \textbf{ {{ project.name }} }{% if project.date_range %} \hfill {{ project.date_range }}{% endif %}
\par
{% if project.achievements %}
\begin{itemize}
{% for achievement in project.achievements %}\item {{ achievement }}
{% endfor %}
\end{itemize}
{% endif %}
{% endfor %}
{% endif %}

{% if certifications %}
\section*{Certifications}
\begin{itemize}
{% for certification in certifications %}\item {{ certification.name }}{% if certification.issuer %} --- {{ certification.issuer }}{% endif %}
{% endfor %}
\end{itemize}
{% endif %}

{% if publications %}
\section*{Publications}
\begin{itemize}
{% for paper in publications %}\item {{ paper.title }}{% if paper.authors %} --- {{ paper.authors }}{% endif %}{% if paper.venue %}, {{ paper.venue }}{% endif %}{% if paper.date %} ({{ paper.date }}){% endif %}
{% endfor %}
\end{itemize}
{% endif %}

{% if awards %}
\section*{Awards}
\begin{itemize}
{% for award in awards %}\item {{ award.title }}{% if award.issuer %} --- {{ award.issuer }}{% endif %}{% if award.date %} ({{ award.date }}){% endif %}
{% endfor %}
\end{itemize}
{% endif %}
"""
