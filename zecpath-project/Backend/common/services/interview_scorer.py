"""
Interview Scoring Service - Aggregate and normalize interview scores
"""
from core.ai_call_models import AIInterviewSession, AIConversationTurn


class InterviewScorer:
    """Calculate aggregate interview scores"""
    
    # Category weights for final score
    CATEGORY_WEIGHTS = {
        'introduction': 0.10,
        'experience': 0.30,
        'skills': 0.35,
        'availability': 0.15,
        'salary': 0.10
    }
    
    @staticmethod
    def calculate_session_score(session_id):
        """Calculate overall interview score for session"""
        try:
            session = AIInterviewSession.objects.get(session_id=session_id)
        except AIInterviewSession.DoesNotExist:
            return None, 'Session not found'
        
        turns = AIConversationTurn.objects.filter(session=session).order_by('turn_number')
        
        if not turns.exists():
            return None, 'No answers found'
        
        # Aggregate by category
        category_scores = InterviewScorer._aggregate_category_scores(turns)
        
        # Calculate weighted final score
        overall_score = InterviewScorer._apply_weights(category_scores)
        
        # Update session
        session.overall_score = overall_score
        session.category_scores = category_scores
        session.save()
        
        return {
            'session_id': session_id,
            'overall_score': round(overall_score, 2),
            'category_scores': category_scores,
            'total_questions': turns.count(),
            'answered_questions': turns.filter(answer_text__isnull=False).exclude(answer_text='').count()
        }, None
    
    @staticmethod
    def _aggregate_category_scores(turns):
        """Aggregate scores by category"""
        category_data = {}
        
        for turn in turns:
            category = turn.category or 'general'
            
            if category not in category_data:
                category_data[category] = {
                    'scores': [],
                    'count': 0
                }
            
            if turn.answer_score is not None:
                category_data[category]['scores'].append(turn.answer_score)
            category_data[category]['count'] += 1
        
        # Calculate averages
        category_scores = {}
        for category, data in category_data.items():
            if data['scores']:
                avg_score = sum(data['scores']) / len(data['scores'])
                category_scores[category] = {
                    'average_score': round(avg_score, 2),
                    'question_count': data['count'],
                    'answered_count': len(data['scores'])
                }
            else:
                category_scores[category] = {
                    'average_score': 0,
                    'question_count': data['count'],
                    'answered_count': 0
                }
        
        return category_scores
    
    @staticmethod
    def _apply_weights(category_scores):
        """Apply category weights to calculate final score"""
        weighted_sum = 0
        
        for category, data in category_scores.items():
            weight = InterviewScorer.CATEGORY_WEIGHTS.get(category, 0.1)
            weighted_sum += data['average_score'] * weight
        
        return weighted_sum
    
    @staticmethod
    def get_score_breakdown(session_id):
        """Get detailed score breakdown"""
        try:
            session = AIInterviewSession.objects.get(session_id=session_id)
        except AIInterviewSession.DoesNotExist:
            return None, 'Session not found'
        
        turns = AIConversationTurn.objects.filter(session=session).order_by('turn_number')
        
        breakdown = []
        for turn in turns:
            breakdown.append({
                'turn_number': turn.turn_number,
                'category': turn.category,
                'question': turn.question_text[:100],
                'answer_score': turn.answer_score,
                'relevance_score': turn.relevance_score,
                'completeness_score': turn.completeness_score,
                'keyword_matches': turn.keyword_matches,
                'confidence_score': turn.confidence_score
            })
        
        return {
            'session_id': session_id,
            'overall_score': session.overall_score,
            'category_scores': session.category_scores,
            'turn_breakdown': breakdown
        }, None
    
    @staticmethod
    def normalize_score(raw_score, min_val=0, max_val=100):
        """Normalize score to 0-100 range"""
        if raw_score < min_val:
            return 0
        if raw_score > max_val:
            return 100
        return ((raw_score - min_val) / (max_val - min_val)) * 100
