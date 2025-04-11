from fastapi import APIRouter, UploadFile, File, HTTPException, status
from io import BytesIO
from PyPDF2 import PdfReader
from backend.core import ai_service
# from backend.api.auth import get_current_user  # If you want to use authentication, uncomment this line

router = APIRouter(prefix="/upload", tags=["resume upload"])

@router.post("/resume-text")
async def upload_resume_and_extract_text(
    file: UploadFile = File(...),
    # current_user = Depends(get_current_user)
):
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported"
        )

    try:
        # Read PDF file and wrap it in BytesIO
        file_bytes = await file.read()
        pdf_reader = PdfReader(BytesIO(file_bytes))
        raw_text = "\n".join(page.extract_text() or "" for page in pdf_reader.pages)

        if not raw_text.strip():
            raise ValueError("No text could be extracted from PDF")

        # Summarize or analyze with OpenAI if needed
        ai_result = ai_service.ai_prompt(
            f"Here is a resume in raw text form:\n\n{raw_text}\n\nClean and reformat this resume in a professional layout."
        )

        return {
            "status": "success",
            "filename": file.filename,
            "extracted_text": ai_result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process PDF: {str(e)}"
        )
