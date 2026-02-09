import re
from collections import Counter

class NLPService:
    """Basic NLP operations for resume parsing"""
    
    @staticmethod
    def tokenize(text):
        """Split text into words/tokens"""
        if not text:
            return []
        # Convert to lowercase and split by non-alphanumeric characters
        tokens = re.findall(r'\b[a-zA-Z0-9+#.]+\b', text.lower())
        return tokens
    
    @staticmethod
    def extract_keywords(text, top_n=20):
        """Extract most frequent keywords"""
        tokens = NLPService.tokenize(text)
        
        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                     'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
                     'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
                     'should', 'could', 'may', 'might', 'must', 'can', 'this', 'that',
                     'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they'}
        
        # Filter tokens
        filtered = [t for t in tokens if t not in stop_words and len(t) > 2]
        
        # Count frequency
        counter = Counter(filtered)
        return counter.most_common(top_n)
    
    @staticmethod
    def extract_emails(text):
        """Extract email addresses"""
        pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        return re.findall(pattern, text)
    
    @staticmethod
    def extract_phones(text):
        """Extract phone numbers"""
        patterns = [
            r'\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # +1-234-567-8900
            r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # (234) 567-8900
            r'\d{10}',  # 2345678900
        ]
        phones = []
        for pattern in patterns:
            phones.extend(re.findall(pattern, text))
        return list(set(phones))
    
    @staticmethod
    def extract_urls(text):
        """Extract URLs"""
        pattern = r'https?://[^\s]+'
        return re.findall(pattern, text)
    
    @staticmethod
    def extract_years_of_experience(text):
        """Extract years of experience mentioned in text"""
        patterns = [
            r'(\d+)\+?\s*(?:years?|yrs?)(?:\s+of)?\s+(?:experience|exp)',
            r'(?:experience|exp)(?:\s+of)?\s+(\d+)\+?\s*(?:years?|yrs?)',
            r'(\d+)\+?\s*(?:years?|yrs?)\s+(?:in|with)',
        ]
        
        years = []
        for pattern in patterns:
            matches = re.findall(pattern, text.lower())
            years.extend([int(y) for y in matches])
        
        return max(years) if years else None
    
    @staticmethod
    def extract_dates(text):
        """Extract date ranges (e.g., 2020-2023, Jan 2020 - Dec 2023)"""
        patterns = [
            r'(\d{4})\s*[-–]\s*(\d{4}|present|current)',
            r'(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+(\d{4})\s*[-–]\s*(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+(\d{4}|present)',
        ]
        
        dates = []
        for pattern in patterns:
            matches = re.findall(pattern, text.lower())
            dates.extend(matches)
        
        return dates
    
    @staticmethod
    def match_patterns(text, patterns):
        """Match multiple regex patterns in text"""
        matches = []
        for pattern in patterns:
            found = re.findall(pattern, text.lower())
            matches.extend(found)
        return list(set(matches))
    
    @staticmethod
    def calculate_match_score(found_items, total_possible):
        """Calculate confidence score"""
        if total_possible == 0:
            return 0.0
        return round(len(found_items) / total_possible, 2)
