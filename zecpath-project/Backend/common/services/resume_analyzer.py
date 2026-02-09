from .resume_parser import ResumeParser
from .nlp_service import NLPService
from .entity_extractors import (
    SkillExtractor, 
    ExperienceExtractor, 
    EducationExtractor, 
    ContactExtractor
)

class ResumeAnalyzer:
    """Main resume analysis orchestrator"""
    
    @staticmethod
    def analyze_resume(file_path):
        """
        Analyze resume and return structured data
        Returns: (structured_data, error)
        """
        # Parse resume text
        raw_text, cleaned_text, error = ResumeParser.parse_resume(file_path)
        
        if error:
            return None, error
        
        # Extract all entities
        skills = SkillExtractor.extract_skills(cleaned_text)
        experience = ExperienceExtractor.extract_experience(cleaned_text)
        education = EducationExtractor.extract_education(cleaned_text)
        contact = ContactExtractor.extract_contact_info(raw_text)
        keywords = NLPService.extract_keywords(cleaned_text, top_n=15)
        
        # Build structured output
        structured_data = {
            'contact_info': contact,
            'skills': {
                'technical': skills['technical'],
                'soft': skills['soft'],
                'certifications': skills['certifications'],
                'all_skills': SkillExtractor.extract_all_skills_flat(cleaned_text)
            },
            'experience': {
                'total_years': experience['total_years'],
                'job_titles': experience['job_titles'],
                'companies': experience['companies'],
                'date_ranges': experience['date_ranges']
            },
            'education': {
                'degrees': education['degrees'],
                'institutions': education['institutions'],
                'graduation_years': education['graduation_years']
            },
            'keywords': [{'word': word, 'frequency': freq} for word, freq in keywords],
            'metadata': {
                'total_skills_found': len(SkillExtractor.extract_all_skills_flat(cleaned_text)),
                'has_email': len(contact['emails']) > 0,
                'has_phone': len(contact['phones']) > 0,
                'has_linkedin': contact['linkedin'] is not None,
                'has_github': contact['github'] is not None,
                'text_length': len(cleaned_text),
                'word_count': len(NLPService.tokenize(cleaned_text))
            },
            'raw_text': raw_text[:500] + '...' if len(raw_text) > 500 else raw_text,  # First 500 chars
            'cleaned_text': cleaned_text[:500] + '...' if len(cleaned_text) > 500 else cleaned_text
        }
        
        return structured_data, None
    
    @staticmethod
    def get_ml_ready_format(structured_data):
        """
        Convert structured data to ML-ready format
        Returns flat feature vector
        """
        if not structured_data:
            return None
        
        ml_format = {
            # Numeric features
            'total_years_experience': structured_data['experience']['total_years'] or 0,
            'total_skills_count': structured_data['metadata']['total_skills_found'],
            'technical_skills_count': len(structured_data['skills']['technical']),
            'soft_skills_count': len(structured_data['skills']['soft']),
            'certifications_count': len(structured_data['skills']['certifications']),
            'education_count': len(structured_data['education']['degrees']),
            'word_count': structured_data['metadata']['word_count'],
            
            # Boolean features
            'has_email': 1 if structured_data['metadata']['has_email'] else 0,
            'has_phone': 1 if structured_data['metadata']['has_phone'] else 0,
            'has_linkedin': 1 if structured_data['metadata']['has_linkedin'] else 0,
            'has_github': 1 if structured_data['metadata']['has_github'] else 0,
            
            # Categorical features (as lists)
            'skills': structured_data['skills']['all_skills'],
            'job_titles': structured_data['experience']['job_titles'],
            'degrees': structured_data['education']['degrees'],
            
            # Text features
            'top_keywords': [kw['word'] for kw in structured_data['keywords'][:10]]
        }
        
        return ml_format
    
    @staticmethod
    def calculate_resume_score(structured_data):
        """
        Calculate overall resume completeness score (0-100)
        """
        if not structured_data:
            return 0
        
        score = 0
        
        # Contact info (20 points)
        if structured_data['metadata']['has_email']:
            score += 5
        if structured_data['metadata']['has_phone']:
            score += 5
        if structured_data['metadata']['has_linkedin']:
            score += 5
        if structured_data['metadata']['has_github']:
            score += 5
        
        # Skills (30 points)
        skills_count = structured_data['metadata']['total_skills_found']
        score += min(30, skills_count * 2)
        
        # Experience (25 points)
        if structured_data['experience']['total_years']:
            score += min(15, structured_data['experience']['total_years'] * 3)
        if structured_data['experience']['job_titles']:
            score += 10
        
        # Education (25 points)
        if structured_data['education']['degrees']:
            score += 15
        if structured_data['education']['institutions']:
            score += 10
        
        return min(100, score)
