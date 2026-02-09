import re
from .nlp_service import NLPService
from .skills_library import (
    TECHNICAL_SKILLS, SOFT_SKILLS, CERTIFICATIONS, 
    JOB_TITLES, DEGREES, get_all_skills
)

class SkillExtractor:
    """Extract skills from resume text"""
    
    @staticmethod
    def extract_skills(text):
        """Match skills from predefined library"""
        text_lower = text.lower()
        found_skills = {
            'technical': [],
            'soft': [],
            'certifications': []
        }
        
        # Match technical skills
        for skill in TECHNICAL_SKILLS:
            if re.search(r'\b' + re.escape(skill) + r'\b', text_lower):
                found_skills['technical'].append(skill)
        
        # Match soft skills
        for skill in SOFT_SKILLS:
            if re.search(r'\b' + re.escape(skill) + r'\b', text_lower):
                found_skills['soft'].append(skill)
        
        # Match certifications
        for cert in CERTIFICATIONS:
            if cert in text_lower:
                found_skills['certifications'].append(cert)
        
        return found_skills
    
    @staticmethod
    def extract_all_skills_flat(text):
        """Return all skills as flat list"""
        categorized = SkillExtractor.extract_skills(text)
        all_skills = []
        for category in categorized.values():
            all_skills.extend(category)
        return list(set(all_skills))


class ExperienceExtractor:
    """Extract work experience information"""
    
    @staticmethod
    def extract_experience(text):
        """Extract experience details"""
        return {
            'total_years': NLPService.extract_years_of_experience(text),
            'job_titles': ExperienceExtractor.extract_job_titles(text),
            'companies': ExperienceExtractor.extract_companies(text),
            'date_ranges': NLPService.extract_dates(text)
        }
    
    @staticmethod
    def extract_job_titles(text):
        """Extract job titles/roles"""
        text_lower = text.lower()
        found_titles = []
        
        for title in JOB_TITLES:
            if re.search(r'\b' + re.escape(title) + r'\b', text_lower):
                found_titles.append(title)
        
        return list(set(found_titles))
    
    @staticmethod
    def extract_companies(text):
        """Extract company names (basic pattern matching)"""
        # Look for patterns like "at CompanyName" or "CompanyName Inc/Ltd/Corp"
        patterns = [
            r'(?:at|@)\s+([A-Z][A-Za-z0-9\s&]+(?:Inc|Ltd|Corp|LLC|Technologies|Systems|Solutions)?)',
            r'([A-Z][A-Za-z0-9\s&]+(?:Inc|Ltd|Corp|LLC|Technologies|Systems|Solutions))',
        ]
        
        companies = []
        for pattern in patterns:
            matches = re.findall(pattern, text)
            companies.extend([m.strip() for m in matches if len(m.strip()) > 2])
        
        # Remove duplicates and common false positives
        companies = list(set(companies))
        return companies[:10]  # Limit to 10


class EducationExtractor:
    """Extract education information"""
    
    @staticmethod
    def extract_education(text):
        """Extract education details"""
        return {
            'degrees': EducationExtractor.extract_degrees(text),
            'institutions': EducationExtractor.extract_institutions(text),
            'graduation_years': EducationExtractor.extract_graduation_years(text)
        }
    
    @staticmethod
    def extract_degrees(text):
        """Extract degree names"""
        text_lower = text.lower()
        found_degrees = []
        
        for degree in DEGREES:
            if re.search(r'\b' + re.escape(degree) + r'\b', text_lower):
                found_degrees.append(degree)
        
        # Also look for specific degree patterns
        degree_patterns = [
            r'(bachelor[\'s]*\s+(?:of\s+)?(?:science|arts|engineering|technology))',
            r'(master[\'s]*\s+(?:of\s+)?(?:science|arts|engineering|technology|business))',
            r'(b\.?tech|m\.?tech|b\.?e\.?|m\.?e\.?|b\.?sc|m\.?sc|mba|bba)',
        ]
        
        for pattern in degree_patterns:
            matches = re.findall(pattern, text_lower)
            found_degrees.extend(matches)
        
        return list(set(found_degrees))
    
    @staticmethod
    def extract_institutions(text):
        """Extract university/college names"""
        # Look for patterns like "University of", "Institute of", college names
        patterns = [
            r'((?:University|College|Institute)\s+of\s+[A-Za-z\s]+)',
            r'([A-Z][A-Za-z\s]+(?:University|College|Institute|School))',
        ]
        
        institutions = []
        for pattern in patterns:
            matches = re.findall(pattern, text)
            institutions.extend([m.strip() for m in matches if len(m.strip()) > 5])
        
        return list(set(institutions))[:5]  # Limit to 5
    
    @staticmethod
    def extract_graduation_years(text):
        """Extract graduation years"""
        # Look for 4-digit years in education context
        pattern = r'(?:graduated|graduation|class of|batch of)?\s*[:\-]?\s*(\d{4})'
        years = re.findall(pattern, text.lower())
        
        # Filter valid years (1970-2030)
        valid_years = [int(y) for y in years if 1970 <= int(y) <= 2030]
        return sorted(set(valid_years))


class ContactExtractor:
    """Extract contact information"""
    
    @staticmethod
    def extract_contact_info(text):
        """Extract all contact information"""
        return {
            'emails': NLPService.extract_emails(text),
            'phones': NLPService.extract_phones(text),
            'urls': NLPService.extract_urls(text),
            'linkedin': ContactExtractor.extract_linkedin(text),
            'github': ContactExtractor.extract_github(text)
        }
    
    @staticmethod
    def extract_linkedin(text):
        """Extract LinkedIn profile URL"""
        pattern = r'(?:https?://)?(?:www\.)?linkedin\.com/in/[\w-]+'
        matches = re.findall(pattern, text.lower())
        return matches[0] if matches else None
    
    @staticmethod
    def extract_github(text):
        """Extract GitHub profile URL"""
        pattern = r'(?:https?://)?(?:www\.)?github\.com/[\w-]+'
        matches = re.findall(pattern, text.lower())
        return matches[0] if matches else None
