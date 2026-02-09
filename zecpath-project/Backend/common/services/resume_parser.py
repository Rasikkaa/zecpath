import os
import re
import pdfplumber
from docx import Document
from PyPDF2 import PdfReader


class ResumeParser:
    """Service for extracting and cleaning text from resumes"""
    
    @staticmethod
    def extract_text(file_path):
        """Extract text from PDF or DOCX file"""
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == '.pdf':
            return ResumeParser._extract_from_pdf(file_path)
        elif ext == '.docx':
            return ResumeParser._extract_from_docx(file_path)
        elif ext == '.doc':
            return None, "DOC format not supported. Please convert to DOCX or PDF"
        else:
            return None, "Unsupported file format"
    
    @staticmethod
    def _extract_from_pdf(file_path):
        """Extract text from PDF using pdfplumber (primary) or PyPDF2 (fallback)"""
        try:
            # Try pdfplumber first (better for structured PDFs)
            with pdfplumber.open(file_path) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() or ""
                
                if text.strip():
                    return text, None
            
            # Fallback to PyPDF2
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            
            if not text.strip():
                return None, "Could not extract text from PDF"
            
            return text, None
            
        except Exception as e:
            return None, f"PDF extraction error: {str(e)}"
    
    @staticmethod
    def _extract_from_docx(file_path):
        """Extract text from DOCX file"""
        try:
            doc = Document(file_path)
            text = "\n".join([para.text for para in doc.paragraphs])
            
            if not text.strip():
                return None, "No text found in DOCX"
            
            return text, None
            
        except Exception as e:
            return None, f"DOCX extraction error: {str(e)}"
    
    @staticmethod
    def clean_text(text):
        """Clean and normalize extracted text"""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s@.,;:()\-+#]', '', text)
        
        # Remove multiple newlines
        text = re.sub(r'\n+', '\n', text)
        
        # Strip leading/trailing whitespace
        text = text.strip()
        
        return text
    
    @staticmethod
    def parse_resume(file_path):
        """Main method: extract and clean text from resume"""
        raw_text, error = ResumeParser.extract_text(file_path)
        
        if error:
            return None, None, error
        
        cleaned_text = ResumeParser.clean_text(raw_text)
        
        return raw_text, cleaned_text, None
