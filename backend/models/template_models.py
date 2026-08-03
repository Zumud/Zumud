"""What the template gallery exchanges with the frontend.

A template is identified by the same slug the database stores, so the client never
has to know the difference between a built-in and one of the user's own — see
`backend.models.templates` for the two forms it takes.
"""

from pydantic import BaseModel


class TemplateSummary(BaseModel):
    slug: str
    name: str
    description: str
    # None until a template has a rendered thumbnail; the client falls back to a
    # placeholder rather than a broken image.
    preview_url: str | None = None
    selected: bool = False
    # "pending" while an upload is being converted, then "ready" or "failed".
    # Built-ins are always ready. The client polls this list to follow an upload.
    status: str
    # Why a conversion failed, meant to be shown to the user as-is.
    error: str | None = None


class TemplateSelection(BaseModel):
    slug: str
