"""
Resume processing module for PDF/DOCX text extraction.
Handles file upload, text extraction, and resume text processing.
"""

import io
import streamlit as st
from typing import Optional, Tuple
from pypdf import PdfReader
from docx import Document
import sys
import os

# Add the Frontend directory to Python path for imports
# Get the directory containing this file (utils), then go up one level (Frontend)
current_file_dir = os.path.dirname(os.path.abspath(__file__))
frontend_dir = os.path.dirname(current_file_dir)
if frontend_dir not in sys.path:
    sys.path.insert(0, frontend_dir)


class ResumeProcessor:
    """Handles resume file processing and text extraction."""
    
    @staticmethod
    def extract_text_from_pdf(file_content: bytes) -> str:
        """
        Extract text from PDF file content.
        
        Args:
            file_content: PDF file content as bytes
            
        Returns:
            Extracted text as string
        """
        try:
            pdf_reader = PdfReader(io.BytesIO(file_content))
            text = ""
            
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            return text.strip()
        except Exception as e:
            st.error(f"Error extracting text from PDF: {e}")
            return ""
    
    @staticmethod
    def extract_text_from_docx(file_content: bytes) -> str:
        """
        Extract text from DOCX file content.
        
        Args:
            file_content: DOCX file content as bytes
            
        Returns:
            Extracted text as string
        """
        try:
            doc = Document(io.BytesIO(file_content))
            text = ""
            
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            return text.strip()
        except Exception as e:
            st.error(f"Error extracting text from DOCX: {e}")
            return ""
    
    @staticmethod
    def extract_text_from_txt(file_content: bytes) -> str:
        """
        Extract text from TXT file content.
        
        Args:
            file_content: TXT file content as bytes
            
        Returns:
            Extracted text as string
        """
        try:
            # Try different encodings
            encodings = ['utf-8', 'latin-1', 'cp1252']
            
            for encoding in encodings:
                try:
                    return file_content.decode(encoding).strip()
                except UnicodeDecodeError:
                    continue
            
            # If all encodings fail, use utf-8 with error handling
            return file_content.decode('utf-8', errors='replace').strip()
            
        except Exception as e:
            st.error(f"Error extracting text from TXT: {e}")
            return ""
    
    @staticmethod
    def process_uploaded_file(uploaded_file) -> Tuple[bool, str]:
        """
        Process uploaded file and extract text.
        
        Args:
            uploaded_file: Streamlit uploaded file object
            
        Returns:
            Tuple of (success, extracted_text)
        """
        if uploaded_file is None:
            return False, ""
        
        try:
            file_content = uploaded_file.read()
            file_extension = uploaded_file.name.split('.')[-1].lower()
            
            if file_extension == 'pdf':
                text = ResumeProcessor.extract_text_from_pdf(file_content)
            elif file_extension == 'docx':
                text = ResumeProcessor.extract_text_from_docx(file_content)
            elif file_extension == 'txt':
                text = ResumeProcessor.extract_text_from_txt(file_content)
            else:
                st.error(f"Unsupported file type: {file_extension}")
                return False, ""
            
            if text:
                st.success(f"Successfully extracted text from {uploaded_file.name}")
                return True, text
            else:
                st.warning(f"No text could be extracted from {uploaded_file.name}")
                return False, ""
                
        except Exception as e:
            st.error(f"Error processing file {uploaded_file.name}: {e}")
            return False, ""
    
    @staticmethod
    def clean_resume_text(text: str) -> str:
        """
        Clean and normalize resume text.
        
        Args:
            text: Raw resume text
            
        Returns:
            Cleaned resume text
        """
        if not text:
            return ""
        
        # Remove excessive whitespace
        import re
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters that might interfere with analysis
        text = re.sub(r'[^\w\s@.-]', ' ', text)
        
        # Remove multiple newlines
        text = re.sub(r'\n+', '\n', text)
        
        return text.strip()
    
    @staticmethod
    def validate_resume_text(text: str) -> Tuple[bool, str]:
        """
        Validate that resume text is suitable for analysis.
        
        Args:
            text: Resume text to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not text or not text.strip():
            return False, "Resume text is empty"
        
        if len(text.strip()) < 50:
            return False, "Resume text is too short (minimum 50 characters)"
        
        if len(text.strip()) > 50000:
            return False, "Resume text is too long (maximum 50,000 characters)"
        
        # Check for common resume keywords
        resume_keywords = ['experience', 'education', 'skills', 'work', 'job', 'position', 'company']
        text_lower = text.lower()
        
        keyword_count = sum(1 for keyword in resume_keywords if keyword in text_lower)
        if keyword_count < 2:
            return False, "Text doesn't appear to be a resume (missing common resume keywords)"
        
        return True, ""


def handle_file_upload(uploaded_file) -> None:
    """
    Handle file upload and update session state.
    This function integrates with Streamlit's session state.
    
    Args:
        uploaded_file: Streamlit uploaded file object
    """
    if uploaded_file is not None:
        success, extracted_text = ResumeProcessor.process_uploaded_file(uploaded_file)
        
        if success:
            # Clean the text
            cleaned_text = ResumeProcessor.clean_resume_text(extracted_text)
            
            # Validate the text
            is_valid, error_msg = ResumeProcessor.validate_resume_text(cleaned_text)
            
            if is_valid:
                st.session_state.raw_resume_text = cleaned_text
                st.success(f"✅ Resume text extracted and ready for analysis!")
                
                # Automatically run analysis to extract personal details
                try:
                    from utils.backend_integration import LocalAnalysisEngine
                    from utils.ui_components import SessionStateManager
                    
                    # Run local analysis to extract personal details
                    analysis_data = LocalAnalysisEngine.analyze_resume_local(
                        resume_text=cleaned_text,
                        positions=st.session_state.get('selected_positions', []),
                        preferences=st.session_state.get('selected_preferences', []),
                        locations=st.session_state.get('preferred_locations', [])
                    )
                    
                    # Update session state with extracted details
                    SessionStateManager.update_session_state_from_analysis(analysis_data)
                    
                    st.info("🔍 Personal details extracted from resume!")
                    
                except Exception as e:
                    st.warning(f"⚠️ Could not extract personal details: {e}")
                    
            else:
                st.warning(f"⚠️ {error_msg}")
                st.session_state.raw_resume_text = cleaned_text  # Still set it, let user decide
        else:
            st.error("❌ Failed to extract text from the uploaded file.")
    else:
        # Clear resume text if no file is uploaded
        if 'raw_resume_text' in st.session_state:
            st.session_state.raw_resume_text = ""
