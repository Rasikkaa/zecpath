"""
Answer Evaluation Service - Score individual interview answers
"""
import re
from collections import Counter


class AnswerEvaluator:
    """Evaluate interview answers for quality and relevance"""
    
    # Category-specific keywords
    CATEGORY_KEYWORDS = {
        'introduction': ['experience', 'background', 'education', 'skills', 'career'],
        'experience': ['years', 'worked', 'project', 'team', 'role', 'responsibility'],
        'skills': ['proficient', 'expert', 'knowledge', 'familiar', 'technology'],
        'availability': ['start', 'notice', 'available', 'join', 'immediately'],
        'salary': ['expectation', 'range', 'compensation', 'package', 'negotiable']
    }
    
    # Minimum word counts for completeness
    MIN_WORDS = {
        'introduction': 20,
        'experience': 15,
        'skills': 10,
        'availability': 5,
        'salary': 5
    }
    
    @staticmethod
    def evaluate_answer(question, answer, category='general', job_context=None):
        """
        Evaluate answer and return scores
        Returns: dict with scores and breakdown
        """
        if not answer or not answer.strip():
            return {
                'answer_score': 0,
                'relevance_score': 0,
                'completeness_score': 0,
                'keyword_matches': {},
                'confidence_score': 0,
                'ai_annotations': {'error': 'Empty answer'}
            }
        
        # Calculate component scores
        relevance = AnswerEvaluator._calculate_relevance(answer, category, question)
        completeness = AnswerEvaluator._calculate_completeness(answer, category)
        keywords = AnswerEvaluator._extract_keyword_matches(answer, category)
        
        # Weighted final score
        answer_score = (relevance * 0.4) + (completeness * 0.3) + (keywords['score'] * 0.3)
        
        # Confidence based on answer length and structure
        confidence = AnswerEvaluator._calculate_confidence(answer)
        
        # AI annotations
        annotations = {
            'word_count': len(answer.split()),
            'has_numbers': bool(re.search(r'\d+', answer)),
            'has_technical_terms': AnswerEvaluator._has_technical_terms(answer),
            'sentiment': 'positive' if any(w in answer.lower() for w in ['yes', 'excited', 'interested']) else 'neutral'
        }
        
        return {
            'answer_score': round(answer_score, 2),
            'relevance_score': round(relevance, 2),
            'completeness_score': round(completeness, 2),
            'keyword_matches': keywords,
            'confidence_score': round(confidence, 2),
            'ai_annotations': annotations
        }
    
    @staticmethod
    def _calculate_relevance(answer, category, question):
        """Score answer relevance to question (0-100)"""
        answer_lower = answer.lower()
        
        # Check for category keywords
        expected_keywords = AnswerEvaluator.CATEGORY_KEYWORDS.get(category, [])
        matches = sum(1 for kw in expected_keywords if kw in answer_lower)
        
        if not expected_keywords:
            return 70  # Default for unknown categories
        
        # Extract question keywords
        question_words = set(re.findall(r'\b\w+\b', question.lower()))
        question_words = {w for w in question_words if len(w) > 3}
        
        answer_words = set(re.findall(r'\b\w+\b', answer_lower))
        overlap = len(question_words & answer_words)
        
        # Combine scores
        keyword_score = (matches / len(expected_keywords)) * 100 if expected_keywords else 50
        overlap_score = min(100, (overlap / max(len(question_words), 1)) * 100)
        
        return (keyword_score * 0.6) + (overlap_score * 0.4)
    
    @staticmethod
    def _calculate_completeness(answer, category):
        """Score answer completeness (0-100)"""
        word_count = len(answer.split())
        min_words = AnswerEvaluator.MIN_WORDS.get(category, 10)
        
        if word_count >= min_words * 2:
            return 100
        elif word_count >= min_words:
            return 80
        elif word_count >= min_words * 0.5:
            return 60
        else:
            return 40
    
    @staticmethod
    def _extract_keyword_matches(answer, category):
        """Extract and score keyword matches"""
        answer_lower = answer.lower()
        expected = AnswerEvaluator.CATEGORY_KEYWORDS.get(category, [])
        
        matched = [kw for kw in expected if kw in answer_lower]
        
        score = (len(matched) / len(expected) * 100) if expected else 50
        
        return {
            'matched': matched,
            'expected': expected,
            'score': score,
            'match_rate': round(len(matched) / len(expected), 2) if expected else 0
        }
    
    @staticmethod
    def _calculate_confidence(answer):
        """Calculate confidence score based on answer quality indicators"""
        score = 50  # Base
        
        # Length bonus
        word_count = len(answer.split())
        if word_count > 30:
            score += 20
        elif word_count > 15:
            score += 10
        
        # Structure bonus
        if '.' in answer or ',' in answer:
            score += 10
        
        # Specificity bonus (numbers, dates)
        if re.search(r'\d+', answer):
            score += 10
        
        # Professional terms
        if AnswerEvaluator._has_technical_terms(answer):
            score += 10
        
        return min(100, score)
    
    @staticmethod
    def _has_technical_terms(answer):
        """Check if answer contains technical/professional terms"""
        technical = ['project', 'team', 'development', 'management', 'analysis', 
                    'implementation', 'design', 'testing', 'deployment']
        return any(term in answer.lower() for term in technical)
