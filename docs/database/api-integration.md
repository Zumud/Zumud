# 🌐 API Integration - Document Tracking Database

## 📋 **Overview**

This document details how database operations are integrated into existing API endpoints to provide comprehensive document tracking without breaking existing functionality.

## 🎯 **Integration Strategy**

### **Principles:**
1. **Zero Breaking Changes**: Existing API contracts remain unchanged
2. **Graceful Degradation**: Database failures don't break API responses
3. **Incremental Integration**: Add database operations after existing logic
4. **Comprehensive Logging**: Track all database operations for debugging

---

## 🔧 **Integration Points**

### **1. Resume Generation Endpoint**

**Endpoint**: `GET /applications/resume/pdf`

**Integration Location**: After successful file generation and cloud storage upload

```python
# Existing logic remains unchanged
latex_compiler_response, tex_content, structured_resume_json = await ai_service.generate_structured_latex_resume_async(...)
pdf_file_path = save_pdf(str(save_path), latex_compiler_response.content, current_user.username)

# Cloud storage upload (existing)
safe_upload_with_fallback(storage_service.upload_tailored_resume, ...)

# NEW: Database integration (after existing logic)
try:
    if job_application:
        # Get cloud storage paths
        cloud_pdf_path = f"users/{current_user.id}/applications/{session_id}_{company_name}/resume.pdf"
        cloud_tex_path = f"users/{current_user.id}/applications/{session_id}_{company_name}/resume.tex"
        
        # Save resume document to database
        DatabaseService.create_resume_document(
            db=db,
            job_application_id=job_application.id,
            user_id=current_user.id,
            content_json=json.loads(structured_resume_json),
            pdf_file_path=cloud_pdf_path,
            tex_file_path=cloud_tex_path,
            local_file_path=str(pdf_file_path),
            generation_time_ms=None
        )
except Exception as e:
    logger.error(f"Database save failed for resume generation: {e}")
    # Continue with response - don't break the API
```

### **2. Cover Letter Generation Endpoint**

**Endpoint**: `GET /applications/cover-letter/plain`

**Integration Location**: After successful file generation and cloud storage upload

```python
# Existing logic remains unchanged
cover_letter_text = ai_service.generate_tailored_coverletter_text(...)
pdf_generator = PDFGenerator()
pdf_path = pdf_generator.create_pdf_document(...)

# Cloud storage upload (existing)
safe_upload_with_fallback(storage_service.upload_cover_letter, ...)

# NEW: Database integration (after existing logic)
try:
    if job_application:
        # Get cloud storage path
        cloud_pdf_path = f"users/{current_user.id}/applications/{session_id}_{company_name}/cover_letter.pdf"
        
        # Save cover letter document to database
        DatabaseService.create_cover_letter_document(
            db=db,
            job_application_id=job_application.id,
            user_id=current_user.id,
            content_text=cover_letter_text,
            pdf_file_path=cloud_pdf_path,
            local_file_path=str(pdf_path),
            generation_time_ms=None
        )
except Exception as e:
    logger.error(f"Database save failed for cover letter generation: {e}")
    # Continue with response - don't break the API
```

### **3. Question Answer Generation Endpoint**

**Endpoint**: `GET /applications/questions/answer`

**Integration Location**: After successful answer generation and cloud storage upload

```python
# Existing logic remains unchanged
answer = ai_service.generate_answer_questions(...)

# Cloud storage upload (existing)
safe_upload_with_fallback(storage_service.upload_question_answer, ...)

# NEW: Database integration (after existing logic)
try:
    if job_application:
        # Save question answer document to database
        DatabaseService.create_question_answer_document(
            db=db,
            job_application_id=job_application.id,
            user_id=current_user.id,
            question=question,
            answer=answer,
            generation_time_ms=None
        )
except Exception as e:
    logger.error(f"Database save failed for question answer: {e}")
    # Continue with response - don't break the API
```

---

## 🔄 **Edit Endpoint Integration**

### **1. Resume Edit Endpoint**

**Endpoint**: `GET /applications/resume/edit`

**Integration Location**: After successful edit generation and cloud storage upload

```python
# Existing logic remains unchanged
latex_compiler_response, updated_resume_json, tex_content = ai_service.update_resume_with_instructions(...)
pdf_file_path = save_pdf(str(new_save_path), latex_compiler_response.content, current_user.username)

# Cloud storage upload (existing)
safe_upload_with_fallback(storage_service.upload_tailored_resume, ...)

# NEW: Database integration (after existing logic)
try:
    if job_application:
        # Get cloud storage paths
        cloud_pdf_path = f"users/{current_user.id}/applications/{session_id}_{company_name}/resume.pdf"
        cloud_tex_path = f"users/{current_user.id}/applications/{session_id}_{company_name}/resume.tex"
        
        # Create new resume document record for this edit
        DatabaseService.create_resume_document(
            db=db,
            job_application_id=job_application.id,
            user_id=current_user.id,
            content_json=json.loads(updated_resume_json),
            pdf_file_path=cloud_pdf_path,
            tex_file_path=cloud_tex_path,
            local_file_path=str(pdf_file_path),
            generation_time_ms=None
        )
        
        # Create edit record
        DatabaseService.create_document_edit(
            db=db,
            document_type='resume',
            document_id=job_application.id,
            user_id=current_user.id,
            edit_instructions=edit_instruction
        )
except Exception as e:
    logger.error(f"Database operations failed for resume edit: {e}")
    # Continue with response - don't break the API
```

### **2. Cover Letter Edit Endpoint**

**Endpoint**: `GET /applications/cover-letter/edit`

**Integration Location**: After successful edit generation and cloud storage upload

```python
# Existing logic remains unchanged
updated_cover_letter = ai_service.update_cover_letter_with_instructions(...)
pdf_generator = PDFGenerator()
new_pdf_file_path = pdf_generator.create_pdf_document(...)

# Cloud storage upload (existing)
safe_upload_with_fallback(storage_service.upload_cover_letter, ...)

# NEW: Database integration (after existing logic)
try:
    if job_application:
        # Get cloud storage path
        cloud_pdf_path = f"users/{current_user.id}/applications/{session_id}_{company_name}/cover_letter.pdf"
        
        # Create new cover letter document record for this edit
        DatabaseService.create_cover_letter_document(
            db=db,
            job_application_id=job_application.id,
            user_id=current_user.id,
            content_text=updated_cover_letter,
            pdf_file_path=cloud_pdf_path,
            local_file_path=str(new_pdf_file_path),
            generation_time_ms=None
        )
        
        # Create edit record
        DatabaseService.create_document_edit(
            db=db,
            document_type='cover_letter',
            document_id=job_application.id,
            user_id=current_user.id,
            edit_instructions=edit_instruction
        )
except Exception as e:
    logger.error(f"Database operations failed for cover letter edit: {e}")
    # Continue with response - don't break the API
```

### **3. Question Answer Edit Endpoint**

**Endpoint**: `GET /applications/questions/answer/edit`

**Integration Location**: After successful edit generation and cloud storage upload

```python
# Existing logic remains unchanged
updated_answer = ai_service.update_answer_with_instructions(...)

# Cloud storage upload (existing)
safe_upload_with_fallback(storage_service.upload_question_answer, ...)

# NEW: Database integration (after existing logic)
try:
    if job_application:
        # Create new question answer document record for this edit
        DatabaseService.create_question_answer_document(
            db=db,
            job_application_id=job_application.id,
            user_id=current_user.id,
            question=question,
            answer=updated_answer,
            generation_time_ms=None
        )
        
        # Create edit record
        DatabaseService.create_document_edit(
            db=db,
            document_type='question_answer',
            document_id=job_application.id,
            user_id=current_user.id,
            edit_instructions=edit_instruction
        )
except Exception as e:
    logger.error(f"Database operations failed for question answer edit: {e}")
    # Continue with response - don't break the API
```

---

## 🆕 **New Query Endpoints**

### **1. Get User Job Applications**

**Endpoint**: `GET /applications/job-applications`

```python
@router.get("/job-applications")
def get_user_job_applications(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = Query(50, description="Maximum number of applications to return")
):
    """Get all job applications for the current user"""
    try:
        applications = DatabaseService.get_user_job_applications(db, current_user.id, limit)
        
        # Convert to dict for JSON serialization
        result = []
        for app in applications:
            result.append({
                "id": app.id,
                "session_id": app.session_id,
                "company_name": app.company_name,
                "job_description": app.job_description,
                "status": app.status,
                "notes": app.notes,
                "created_at": app.created_at.isoformat() if app.created_at else None,
                "updated_at": app.updated_at.isoformat() if app.updated_at else None
            })
        
        return {"applications": result}
    except Exception as e:
        logger.error(f"Failed to get job applications: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve job applications"
        )
```

### **2. Get Job Application Documents**

**Endpoint**: `GET /applications/job-applications/{application_id}/documents`

```python
@router.get("/job-applications/{application_id}/documents")
def get_job_application_documents(
    application_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all documents for a specific job application"""
    try:
        # Verify the application belongs to the current user
        job_application = DatabaseService.get_job_application_by_session_id(db, application_id)
        if not job_application or job_application.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job application not found"
            )
        
        documents = DatabaseService.get_job_application_documents(db, job_application.id)
        
        # Convert to dict for JSON serialization
        result = {}
        for doc_type, doc_list in documents.items():
            result[doc_type] = []
            for doc in doc_list:
                doc_dict = {
                    "id": doc.id,
                    "created_at": doc.created_at.isoformat() if doc.created_at else None,
                    "edit_count": doc.edit_count,
                    "last_edited_at": doc.last_edited_at.isoformat() if doc.last_edited_at else None
                }
                
                # Add type-specific fields
                if hasattr(doc, 'content_json'):
                    doc_dict["content_json"] = doc.content_json
                if hasattr(doc, 'content_text'):
                    doc_dict["content_text"] = doc.content_text
                if hasattr(doc, 'question'):
                    doc_dict["question"] = doc.question
                if hasattr(doc, 'answer'):
                    doc_dict["answer"] = doc.answer
                if hasattr(doc, 'pdf_file_path'):
                    doc_dict["pdf_file_path"] = doc.pdf_file_path
                if hasattr(doc, 'tex_file_path'):
                    doc_dict["tex_file_path"] = doc.tex_file_path
                if hasattr(doc, 'local_file_path'):
                    doc_dict["local_file_path"] = doc.local_file_path
                
                result[doc_type].append(doc_dict)
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get job application documents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve job application documents"
        )
```

### **3. Update Job Application Status**

**Endpoint**: `PUT /applications/job-applications/{application_id}/status`

```python
@router.put("/job-applications/{application_id}/status")
def update_job_application_status(
    application_id: str,
    status: str = Query(..., description="New status for the application"),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update the status of a job application"""
    try:
        # Verify the application belongs to the current user
        job_application = DatabaseService.get_job_application_by_session_id(db, application_id)
        if not job_application or job_application.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job application not found"
            )
        
        # Validate status
        valid_statuses = ['draft', 'submit', 'interview', 'offer', 'rejected']
        if status not in valid_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Must be one of: {valid_statuses}"
            )
        
        updated_application = DatabaseService.update_job_application_status(db, job_application.id, status)
        
        return {
            "id": updated_application.id,
            "session_id": updated_application.session_id,
            "status": updated_application.status,
            "updated_at": updated_application.updated_at.isoformat() if updated_application.updated_at else None
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update job application status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update job application status"
        )
```

---

## 🛡️ **Error Handling Strategy**

### **Database Operation Failures:**
- **Wrapped in try-catch blocks** around all database operations
- **Logged for debugging** but don't break API responses
- **Graceful degradation** - API continues to work without database tracking
- **No user-facing errors** from database failures

### **Validation Failures:**
- **Proper HTTP status codes** for different error types
- **Meaningful error messages** for debugging
- **Input validation** for all new endpoints
- **Authorization checks** for data access

### **Performance Considerations:**
- **Database operations are non-blocking** for API responses
- **Async operations** where possible
- **Connection pooling** for database efficiency
- **Indexed queries** for performance

---

## 📊 **Integration Benefits**

### **For Existing Endpoints:**
- ✅ **No Breaking Changes**: All existing functionality preserved
- ✅ **Enhanced Tracking**: Complete audit trail added
- ✅ **Better Debugging**: Rich logging for troubleshooting
- ✅ **Future Ready**: Foundation for advanced features

### **For New Endpoints:**
- ✅ **Rich Data Access**: Complete document and application history
- ✅ **User Management**: Application lifecycle tracking
- ✅ **Analytics Ready**: Data for user behavior analysis
- ✅ **Scalable Design**: Built for future enhancements

---

## ✅ **Integration Checklist**

### **Before Integration:**
- [ ] Database models created and tested
- [ ] Database service implemented and tested
- [ ] Error handling strategy defined
- [ ] Logging configuration updated

### **During Integration:**
- [ ] Add database operations after existing logic
- [ ] Wrap all database operations in try-catch
- [ ] Add comprehensive logging
- [ ] Test error scenarios

### **After Integration:**
- [ ] Verify existing functionality unchanged
- [ ] Test new query endpoints
- [ ] Monitor database performance
- [ ] Validate data consistency

---

## 🚀 **Ready for Integration**

The API integration design is:
- ✅ **Non-Breaking**: Preserves all existing functionality
- ✅ **Comprehensive**: Covers all generation and edit endpoints
- ✅ **Robust**: Proper error handling and logging
- ✅ **Scalable**: Built for future enhancements
- ✅ **Tested**: Clear testing strategy defined

**Next Steps**: Follow the implementation plan in `docs/database/implementation-plan.md` to integrate these database operations into the existing API endpoints. 