from core.question_models import QuestionTemplate, QuestionFlow, InterviewState
from core.ai_call_models import AIInterviewSession
import logging

logger = logging.getLogger(__name__)


class QuestionEngineService:
    """Dynamic question flow engine with branching logic"""
    
    @staticmethod
    def initialize_flow(session, job):
        """Initialize interview state"""
        state = InterviewState.objects.create(
            session=session,
            current_question_index=0,
            context={'job_id': job.id, 'answers': {}}
        )
        return state
    
    @staticmethod
    def get_next_question(state, previous_answer=None):
        """Get next question based on state and previous answer"""
        session = state.session
        job = session.call_queue.application.job
        
        # Store previous answer
        if previous_answer:
            state.context['answers'][state.current_question_index] = previous_answer
            state.save()
        
        # Get question flow for job
        flows = QuestionFlow.objects.filter(job=job).select_related('template')
        
        if not flows.exists():
            # Fallback: use default templates
            flows = QuestionEngineService._get_default_flow(job)
        else:
            flows = list(flows)
        
        # Check if interview complete
        if state.current_question_index >= len(flows):
            return None, 'completed'
        
        # Get current question
        flow = flows[state.current_question_index]
        template = flow.template
        
        # Check conditions
        if not QuestionEngineService._check_conditions(template, state.context):
            # Skip this question
            state.current_question_index += 1
            state.save()
            return QuestionEngineService.get_next_question(state)
        
        # Check for follow-up
        follow_up = QuestionEngineService._check_follow_up(template, previous_answer)
        if follow_up:
            return follow_up, template.category
        
        # Mark category as completed
        if template.category not in state.completed_categories:
            state.completed_categories.append(template.category)
            state.save()
        
        return template.question_text, template.category
    
    @staticmethod
    def advance_state(state):
        """Move to next question"""
        state.current_question_index += 1
        state.save()
    
    @staticmethod
    def _check_conditions(template, context):
        """Check if question should be asked based on conditions"""
        if not template.condition:
            return True
        
        answers = context.get('answers', {})
        
        # Example: {"min_experience": 3}
        if 'min_experience' in template.condition:
            exp = QuestionEngineService._extract_experience(answers)
            if exp < template.condition['min_experience']:
                return False
        
        # Example: {"requires_skill": "python"}
        if 'requires_skill' in template.condition:
            skill = template.condition['requires_skill'].lower()
            if not any(skill in str(ans).lower() for ans in answers.values()):
                return False
        
        return True
    
    @staticmethod
    def _check_follow_up(template, answer):
        """Check if follow-up question needed"""
        if not template.follow_up_trigger or not answer:
            return None
        
        triggers = template.follow_up_trigger.get('keywords', [])
        answer_lower = answer.lower()
        
        for keyword in triggers:
            if keyword.lower() in answer_lower:
                # Generate follow-up
                return f"You mentioned {keyword}. Can you tell me more about your experience with it?"
        
        return None
    
    @staticmethod
    def _extract_experience(answers):
        """Extract years of experience from answers"""
        import re
        for answer in answers.values():
            match = re.search(r'(\d+)\s*(?:years?|yrs?)', str(answer).lower())
            if match:
                return int(match.group(1))
        return 0
    
    @staticmethod
    def _get_default_flow(job):
        """Get default question templates if no custom flow"""
        templates = QuestionTemplate.objects.filter(
            is_active=True,
            role__in=['', job.title]
        ).order_by('category', 'order')
        
        if not templates.exists():
            # Create basic templates
            QuestionEngineService._create_default_templates()
            templates = QuestionTemplate.objects.filter(is_active=True)
        
        # Create temporary flow objects
        return [type('Flow', (), {'template': t, 'order': i, 'is_required': True})() 
                for i, t in enumerate(templates)]
    
    @staticmethod
    def _create_default_templates():
        """Create default question templates"""
        defaults = [
            {'category': 'introduction', 'question_text': 'Tell me about yourself and your background.', 'order': 1},
            {'category': 'experience', 'question_text': 'How many years of professional experience do you have?', 'order': 2},
            {'category': 'skills', 'question_text': 'What are your key technical skills?', 'order': 3},
            {'category': 'availability', 'question_text': 'When can you start if selected?', 'order': 4},
            {'category': 'salary', 'question_text': 'What are your salary expectations?', 'order': 5},
        ]
        
        for data in defaults:
            QuestionTemplate.objects.get_or_create(**data)
