from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from core.permissions import IsEmployer, IsAdmin
from core.question_models import QuestionTemplate, QuestionFlow, InterviewState
from employers.models import Job
from common.utils.pagination import paginate_queryset


class QuestionTemplateListAPI(APIView):
    permission_classes = [IsEmployer | IsAdmin]
    
    def get(self, request):
        """List all question templates"""
        templates = QuestionTemplate.objects.filter(is_active=True)
        
        category = request.GET.get('category')
        if category:
            templates = templates.filter(category=category)
        
        result = paginate_queryset(templates, request)
        
        data = [{
            'id': t.id,
            'category': t.category,
            'question_text': t.question_text,
            'role': t.role,
            'order': t.order,
            'condition': t.condition,
            'follow_up_trigger': t.follow_up_trigger
        } for t in result['page_obj']]
        
        result['results'] = data
        del result['page_obj']
        
        return Response(result)
    
    def post(self, request):
        """Create custom question template"""
        data = request.data
        
        template = QuestionTemplate.objects.create(
            category=data.get('category'),
            question_text=data.get('question_text'),
            role=data.get('role', ''),
            condition=data.get('condition', {}),
            follow_up_trigger=data.get('follow_up_trigger', {}),
            order=data.get('order', 0)
        )
        
        return Response({
            'id': template.id,
            'message': 'Template created'
        }, status=status.HTTP_201_CREATED)


class JobQuestionFlowAPI(APIView):
    permission_classes = [IsEmployer | IsAdmin]
    
    def get(self, request, job_id):
        """Get question flow for job"""
        try:
            if request.user.role == 'employer':
                job = Job.objects.get(id=job_id, employer__user=request.user)
            else:
                job = Job.objects.get(id=job_id)
            
            flows = QuestionFlow.objects.filter(job=job).select_related('template')
            
            data = [{
                'order': f.order,
                'category': f.template.category,
                'question': f.template.question_text,
                'is_required': f.is_required
            } for f in flows]
            
            return Response({'job_id': job_id, 'questions': data})
            
        except Job.DoesNotExist:
            return Response({'error': 'Job not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def post(self, request, job_id):
        """Set question flow for job"""
        try:
            if request.user.role == 'employer':
                job = Job.objects.get(id=job_id, employer__user=request.user)
            else:
                job = Job.objects.get(id=job_id)
            
            template_ids = request.data.get('template_ids', [])
            
            # Clear existing flow
            QuestionFlow.objects.filter(job=job).delete()
            
            # Create new flow
            for order, template_id in enumerate(template_ids, 1):
                template = QuestionTemplate.objects.get(id=template_id)
                QuestionFlow.objects.create(
                    job=job,
                    template=template,
                    order=order
                )
            
            return Response({'message': 'Question flow updated'})
            
        except Job.DoesNotExist:
            return Response({'error': 'Job not found'}, status=status.HTTP_404_NOT_FOUND)


class InterviewStateAPI(APIView):
    permission_classes = [IsEmployer | IsAdmin]
    
    def get(self, request, session_id):
        """Get interview state"""
        try:
            from core.ai_call_models import AIInterviewSession
            
            session = AIInterviewSession.objects.get(session_id=session_id)
            
            if request.user.role == 'employer':
                if session.call_queue.application.job.employer.user != request.user:
                    return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
            
            state = InterviewState.objects.get(session=session)
            
            return Response({
                'session_id': session_id,
                'current_question_index': state.current_question_index,
                'completed_categories': state.completed_categories,
                'context': state.context
            })
            
        except (AIInterviewSession.DoesNotExist, InterviewState.DoesNotExist):
            return Response({'error': 'State not found'}, status=status.HTTP_404_NOT_FOUND)
