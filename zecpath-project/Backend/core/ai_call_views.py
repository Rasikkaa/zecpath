from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import models
from core.permissions import IsEmployer, IsAdmin
from core.ai_call_models import AICallQueue, AIInterviewSession, AIConversationTurn
from core.models import Application
from common.tasks_ai_calls import schedule_ai_call_task
from common.utils.pagination import paginate_queryset

class AICallQueueListAPI(APIView):
    permission_classes = [IsEmployer | IsAdmin]
    
    def get(self, request):
        """Get AI call queue for employer's jobs"""
        if request.user.role == 'employer':
            calls = AICallQueue.objects.filter(
                application__job__employer__user=request.user
            ).select_related('application__candidate__user', 'application__job')
        else:
            calls = AICallQueue.objects.all().select_related(
                'application__candidate__user', 'application__job'
            )
        
        # Filter by status
        status_filter = request.GET.get('status')
        if status_filter:
            calls = calls.filter(status=status_filter)
        
        result = paginate_queryset(calls, request)
        
        data = [{
            'id': call.id,
            'candidate': call.application.candidate.user.email,
            'job': call.application.job.title,
            'status': call.status,
            'scheduled_at': call.scheduled_at,
            'started_at': call.started_at,
            'completed_at': call.completed_at,
            'retry_count': call.retry_count,
            'call_duration': call.call_duration,
            'triggered_by': call.triggered_by.email if call.triggered_by else 'System',
            'trigger_reason': call.trigger_reason,
            'call_outcome': call.call_outcome,
            'sentiment_score': call.sentiment_score,
        } for call in result['page_obj']]
        
        result['results'] = data
        del result['page_obj']
        
        return Response(result)

class AICallTriggerAPI(APIView):
    permission_classes = [IsEmployer | IsAdmin]
    
    def post(self, request, application_id):
        """Manually trigger AI call for application"""
        try:
            if request.user.role == 'employer':
                application = Application.objects.get(
                    id=application_id,
                    job__employer__user=request.user
                )
            else:
                application = Application.objects.get(id=application_id)
            
            # Trigger async task with manual trigger info
            result = schedule_ai_call_task.delay(
                application_id,
                triggered_by_id=request.user.id,
                trigger_reason='manual'
            )
            
            return Response({
                'message': 'AI call scheduled',
                'task_id': result.id
            }, status=status.HTTP_202_ACCEPTED)
            
        except Application.DoesNotExist:
            return Response({'error': 'Application not found'}, status=status.HTTP_404_NOT_FOUND)

class AICallStatsAPI(APIView):
    permission_classes = [IsEmployer | IsAdmin]
    
    def get(self, request):
        """Get AI call statistics"""
        if request.user.role == 'employer':
            calls = AICallQueue.objects.filter(
                application__job__employer__user=request.user
            )
        else:
            calls = AICallQueue.objects.all()
        
        stats = {
            'total': calls.count(),
            'queued': calls.filter(status='queued').count(),
            'in_progress': calls.filter(status='in_progress').count(),
            'completed': calls.filter(status='completed').count(),
            'failed': calls.filter(status='failed').count(),
            'avg_duration': calls.filter(
                status='completed',
                call_duration__isnull=False
            ).aggregate(avg=models.Avg('call_duration'))['avg'] or 0
        }
        
        return Response(stats)


class AIConversationDetailAPI(APIView):
    permission_classes = [IsEmployer | IsAdmin]
    
    def get(self, request, call_id):
        """Get full conversation details"""
        try:
            if request.user.role == 'employer':
                call = AICallQueue.objects.get(
                    id=call_id,
                    application__job__employer__user=request.user
                )
            else:
                call = AICallQueue.objects.get(id=call_id)
            
            # Get session if exists
            try:
                session = call.session
                turns = AIConversationTurn.objects.filter(session=session).order_by('turn_number')
                
                return Response({
                    'call_id': call.id,
                    'session_id': session.session_id,
                    'status': call.status,
                    'outcome': call.call_outcome,
                    'summary': call.conversation_summary,
                    'sentiment': call.sentiment_score,
                    'transcript': session.full_transcript_text,
                    'overall_score': session.overall_score,
                    'category_scores': session.category_scores,
                    'turns': [{
                        'turn': turn.turn_number,
                        'category': turn.category,
                        'question': turn.question_text,
                        'answer': turn.answer_text,
                        'duration': turn.duration_seconds,
                        'scores': {
                            'answer_score': turn.answer_score,
                            'relevance': turn.relevance_score,
                            'completeness': turn.completeness_score,
                            'confidence': turn.confidence_score
                        },
                        'keyword_matches': turn.keyword_matches
                    } for turn in turns],
                    'metadata': {
                        'triggered_by': call.triggered_by.email if call.triggered_by else 'System',
                        'trigger_reason': call.trigger_reason,
                        'scheduled_at': call.scheduled_at,
                        'started_at': call.started_at,
                        'completed_at': call.completed_at,
                        'duration': call.call_duration
                    }
                })
            except AIInterviewSession.DoesNotExist:
                return Response({
                    'call_id': call.id,
                    'status': call.status,
                    'message': 'No conversation data yet'
                })
                
        except AICallQueue.DoesNotExist:
            return Response({'error': 'Call not found'}, status=status.HTTP_404_NOT_FOUND)
