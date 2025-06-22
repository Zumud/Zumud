from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Enum, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from backend.models.db import Base
from backend.models.ai_models import AIModel
from backend.models.templates import ResumeTemplate

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    email = Column(String, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Establish relationships
    resumes = relationship("Resume", back_populates="user", uselist=False)
    legal_authorization = relationship("LegalAuthorization", back_populates="user", uselist=False)
    tailoring_options = relationship("TailoringOptions", back_populates="user", uselist=False)
    preferences = relationship("UserPreferences", back_populates="user", uselist=False)
    templates = relationship("UserTemplate", back_populates="user")

class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    resume_content = Column(Text, nullable=True)  # Allow null for users without resume content
    resume_file_path = Column(String, nullable=True)  # Path to the uploaded PDF file
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Establish relationship with User
    user = relationship("User", back_populates="resumes")

class LegalAuthorization(Base):
    __tablename__ = "legal_authorizations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    work_authorization = Column(Text, nullable=False)
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Establish relationship with User
    user = relationship("User", back_populates="legal_authorization")

class TailoringOptions(Base):
    __tablename__ = "tailoring_options"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    ai_model = Column(Enum(AIModel), nullable=False, default=AIModel.gpt_4_1_nano)
    resume_template = Column(Enum(ResumeTemplate), nullable=False, default=ResumeTemplate.MTeck_resume)
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Establish relationship with User
    user = relationship("User", back_populates="tailoring_options")

class UserPreferences(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    preferences_text = Column(Text, nullable=False, default="")
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Establish relationship with User
    user = relationship("User", back_populates="preferences")

class UserTemplate(Base):
    __tablename__ = "user_templates"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    name = Column(String, nullable=False)  # User-friendly name for the template
    latex_content = Column(Text, nullable=False)  # The actual LaTeX template content
    compiler = Column(String, nullable=False, default="pdflatex")  # LaTeX compiler to use
    is_active = Column(Boolean, nullable=False, default=True)  # Whether this template is currently active
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Establish relationship with User
    user = relationship("User", back_populates="templates") 