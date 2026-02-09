"""
Answer Scoring API Views
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from core.permissions import IsEmployer, IsAdmin
from core.ai_call_models import AIConversationTurn, AIInterviewSession
from common.services.answer_evaluator import AnswerEvaluator
from common.services.interview_scorer import InterviewScorer


class AnswerSubmitAPI(APIView):
    permission_classes = [IsEmployer | IsAdmin]
    
    def post(self, request):
        """Submit/update answer with evaluation"""
        turn_id = request.data.get('turn_id')
        answer_text = request.data.get('answer')
        
        if not turn_id or not answer_text:
            return Response({'error': 'turn_id and answer required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            turn = AIConversationTurn.objects.get(id=turn_id)
            
            # Update answer
            turn.answer_text = answer_text
            
            # Evaluate answer
            evaluation = AnswerEvaluator.evaluate_answer(
                question=turn.question_text,
                answer=answer_text,
                category=turn.category or 'general'
            )
            
            # Store scores
            turn.answer_score = evaluation['answer_score']
            turn.relevance_score = evaluation['relevance_score']
            turn.completeness_score = evaluation['completeness_score']
            turn.keyword_matches = evaluation['keyword_matches']
            turn.confidence_score = evaluation['confidence_score']
            turn.ai_annotations = evaluation['ai_annotations']
            turn.save()
            
            return Response({
                'message': 'Answer evaluated',
                'turn_id': turn_id,
                'scores': evaluation
            }, status=status.HTTP_200_OK)
            
        except AIConversationTurn.DoesNotExist:
            return Response({'error': 'Turn not found'}, status=status.HTTP_404_NOT_FOUND)


class AnswerScoreAPI(APIView):
    permission_classes = [IsEmployer | IsAdmin]
    
    def get(self, request, turn_id):
        """Get individual answer score"""
        try:
            turn = AIConversationTurn.objects.get(id=turn_id)
            
            return Response({
                'turn_id': turn_id,
                'turn_number': turn.turn_number,
                'category': turn.category,
                'question': turn.question_text,
                'answer': turn.answer_text,
                'scores': {
                    'answer_score': turn.answer_score,
                    'relevance_score': turn.relevance_score,
                    'completeness_score': turn.completeness_score,
                    'confidence_score': turn.confidence_score
                },
                'keyword_matches': turn.keyword_matches,
                'ai_annotations': turn.ai_annotations
            })
            
        except AIConversationTurn.DoesNotExist:
            return Response({'error': 'Turn not found'}, status=status.HTTP_404_NOT_FOUND)


class SessionScoresAPI(APIView):
    permission_classes = [IsEmployer | IsAdmin]
    
    def get(self, request, session_id):
        """Get all scores for interview session"""
        breakdown, error = InterviewScorer.get_score_breakdown(session_id)
        
        if error:
            return Response({'error': error}, status=status.HTTP_404_NOT_FOUND)
        
        return Response(breakdown)


class AggregateScoreAPI(APIView):
    permission_classes = [IsEmployer | IsAdmin]
    
    def get(self, request, session_id):
        """Get final aggregate interview score"""
        result, error = InterviewScorer.calculate_session_score(session_id)
        
        if error:
            return Response({'error': error}, status=status.HTTP_404_NOT_FOUND)
        
        return Response(result)
    
    def post(self, request, session_id):
        """Recalculate aggregate score"""
        result, error = InterviewScorer.calculate_session_score(session_id)
        
        if error:
            return Response({'error': error}, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            'message': 'Score recalculated',
            **result
        })
