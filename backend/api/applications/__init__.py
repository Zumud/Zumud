"""Job-application endpoints, split by resource.

URLs are unchanged from the original single-module router: everything lives
under the /applications prefix.
"""

from fastapi import APIRouter

from backend.api.applications import anonymous, cover_letters, questions, resumes

router = APIRouter(prefix="/applications", tags=["applications"])
router.include_router(resumes.router)
router.include_router(cover_letters.router)
router.include_router(questions.router)
router.include_router(anonymous.router)
