from dataclasses import dataclass, field

from .legal_authorization_models import LegalAuthorization


@dataclass
class Resume:
    text: str


@dataclass
class Profile:
    resume: Resume = field(default_factory=Resume)
    legal_authorization: LegalAuthorization = None
    username: str = None
