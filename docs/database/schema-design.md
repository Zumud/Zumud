# 🗄️ Database Schema Design - Document Tracking

## 📋 **Overview**

This document outlines the database schema design for tracking generated documents (resumes, cover letters, Q&As) and job applications. The design focuses on simplicity, zero-logic integration, and complete audit trails.

## 🎯 **Design Principles**

1. **Zero New Logic**: Every field maps directly to existing code/data
2. **Drop-In Integration**: Can add DB inserts without changing existing flows
3. **Complete Tracking**: Every document generation and edit is tracked
4. **Application Context**: All documents linked to specific job applications
5. **Future Ready**: Simple structure can be extended later

---

## 📊 **Database Tables**

### **1. `job_applications` (Application Sessions)**

```sql
job_applications:
- id (UUID, Primary Key)
- user_id (FK to users)
- session_id (UUID) -- matches our file system UUIDs
- company_name (VARCHAR, nullable) -- from ai_service.get_company_name()
- job_description (TEXT) -- direct from API parameter
- status (ENUM: 'draft', 'submit', 'interview', 'offer', 'rejected')
- notes (TEXT, nullable)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)

Indexes: user_id, session_id, status, created_at
```

**Purpose**: Track job application sessions and lifecycle status.

### **2. `resume_documents` (Resume Documents)**

```sql
resume_documents:
- id (UUID, Primary Key)
- job_application_id (FK to job_applications)
- user_id (FK to users)
- content_json (JSONB) -- structured resume JSON we already generate
- pdf_file_path (VARCHAR) -- cloud storage path we already have
- tex_file_path (VARCHAR, nullable) -- cloud storage path we already have
- local_file_path (VARCHAR, nullable) -- local path we already have
- generation_time_ms (INTEGER, nullable)
- edit_count (INTEGER, default 0)
- last_edited_at (TIMESTAMP, nullable)
- created_at (TIMESTAMP)

Indexes: job_application_id, user_id, created_at
```

**Purpose**: Track resume generations and versions.

### **3. `cover_letters` (Cover Letter Documents)**

```sql
cover_letters:
- id (UUID, Primary Key)
- job_application_id (FK to job_applications)
- user_id (FK to users)
- content_text (TEXT) -- plain text content we already generate
- pdf_file_path (VARCHAR) -- cloud storage path we already have
- local_file_path (VARCHAR, nullable) -- local path we already have
- generation_time_ms (INTEGER, nullable)
- edit_count (INTEGER, default 0)
- last_edited_at (TIMESTAMP, nullable)
- created_at (TIMESTAMP)

Indexes: job_application_id, user_id, created_at
```

**Purpose**: Track cover letter generations and versions.

### **4. `question_answers` (Application Q&As)**

```sql
question_answers:
- id (UUID, Primary Key)
- job_application_id (FK to job_applications)
- user_id (FK to users)
- question (TEXT) -- direct from API parameter
- answer (TEXT) -- AI-generated answer we already create
- generation_time_ms (INTEGER, nullable)
- edit_count (INTEGER, default 0)
- last_edited_at (TIMESTAMP, nullable)
- created_at (TIMESTAMP)

Indexes: job_application_id, user_id, created_at
```

**Purpose**: Track Q&A generations and versions.

### **5. `document_edits` (Simple Edit Tracking - OPTIONAL)**

```sql
document_edits:
- id (UUID, Primary Key)
- document_type (ENUM: 'resume', 'cover_letter', 'question_answer')
- document_id (UUID)
- user_id (FK to users)
- edit_instructions (TEXT) -- direct from API parameter
- created_at (TIMESTAMP)

Indexes: document_id, document_type, created_at
```

**Purpose**: Track edit history across document types.

---

## 🔗 **Relationships**

```
users (1) ←→ (many) job_applications
job_applications (1) ←→ (many) resume_documents
job_applications (1) ←→ (many) cover_letters
job_applications (1) ←→ (many) question_answers
users (1) ←→ (many) document_edits
```

---

## 📊 **Status Workflow**

```
draft → submit → interview → offer ✅
   ↓       ↓        ↓
rejected ← rejected ← rejected
```

**Status Meanings:**
- **`draft`**: Application being prepared (default)
- **`submit`**: Application submitted to company
- **`interview`**: Interview scheduled/completed
- **`offer`**: Job offer received
- **`rejected`**: Application unsuccessful (at any stage)

---

## 🔄 **Data Mapping**

### **From Current API Calls:**
- `job_description` ← API parameter
- `question` ← API parameter  
- `edit_instructions` ← API parameter
- `user_id` ← `current_user.id`

### **From Current Services:**
- `company_name` ← `ai_service.get_company_name(job_description)`
- `content_json` ← `structured_resume_json` (already generated)
- `content_text` ← cover letter text (already generated)
- `answer` ← Q&A answer (already generated)

### **From Current File System:**
- `session_id` ← Our existing UUID system
- `pdf_file_path` ← Supabase paths we already create
- `tex_file_path` ← Supabase paths we already create
- `local_file_path` ← Local paths we already create

---

## 🚀 **Implementation Benefits**

### **1. Direct Field Population**
```python
# All data we already have - no new logic needed!
job_application = JobApplication(
    user_id=current_user.id,
    session_id=session_id,  # We already generate this
    company_name=company_name,  # We already extract this
    job_description=job_description,  # API parameter
    status='draft'  # Simple default
)

resume = ResumeDocument(
    job_application_id=job_application.id,
    user_id=current_user.id,
    content_json=structured_resume_json,  # We already generate this
    pdf_file_path=cloud_pdf_path,  # We already create this
    tex_file_path=cloud_tex_path,  # We already create this
    local_file_path=local_path  # We already create this
)
```

### **2. Simple Query Patterns**
```sql
-- User's applications (dashboard)
SELECT * FROM job_applications WHERE user_id = ? ORDER BY created_at DESC

-- Application documents
SELECT * FROM resume_documents WHERE job_application_id = ?
SELECT * FROM cover_letters WHERE job_application_id = ?
SELECT * FROM question_answers WHERE job_application_id = ?

-- Recent activity
SELECT 'resume' as type, created_at FROM resume_documents WHERE user_id = ?
UNION ALL
SELECT 'cover_letter', created_at FROM cover_letters WHERE user_id = ?
ORDER BY created_at DESC
```

---

## 📈 **Future Extensions**

### **Potential Enhancements:**
1. **Performance Metrics**: Track generation times and success rates
2. **Template Usage**: Track which templates are most effective
3. **User Analytics**: Understand user behavior and preferences
4. **A/B Testing**: Compare different AI models and approaches
5. **Export Features**: Generate reports and analytics

### **Scalability Considerations:**
- UUID primary keys for distributed systems
- Proper indexing for query performance
- JSONB for flexible structured data
- Timestamp-based versioning for audit trails

---

## ✅ **Ready for Implementation**

This schema design is:
- ✅ **Zero Logic**: Every field maps to existing code
- ✅ **Drop-In**: Can be integrated without breaking changes
- ✅ **Complete**: Tracks all document lifecycle events
- ✅ **Scalable**: Designed for future growth
- ✅ **Maintainable**: Simple relationships and clear purpose

**Next Steps**: See `implementation-plan.md` for step-by-step implementation guide. 