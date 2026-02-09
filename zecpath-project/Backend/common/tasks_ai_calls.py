from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

@shared_task(name='schedule_ai_call')
def schedule_ai_call_task(application_id, triggered_by_id=None, trigger_reason='auto'):
    """Schedule AI call for eligible application"""
    from core.models import Application, CustomUser
    from core.ai_call_models import AICallQueue
    from common.services.ai_call_eligibility import AICallEligibility
    
    try:
        application = Application.objects.get(id=application_id)
        
        # Check eligibility
        is_eligible, checks = AICallEligibility.is_eligible(application)
        
        if not is_eligible:
            logger.info(f"Application {application_id} not eligible: {checks}")
            return {'status': 'not_eligible', 'checks': checks}
        
        # Get next call slot
        scheduled_at = AICallEligibility.get_next_call_slot()
        
        # Get triggered_by user
        triggered_by = None
        if triggered_by_id:
            try:
                triggered_by = CustomUser.objects.get(id=triggered_by_id)
            except CustomUser.DoesNotExist:
                pass
        
        # Create call queue entry with audit info
        call_queue = AICallQueue.objects.create(
            application=application,
            scheduled_at=scheduled_at,
            status='queued',
            triggered_by=triggered_by,
            trigger_reason=trigger_reason
        )
        
        # Schedule execution
        execute_ai_call_task.apply_async(
            args=[call_queue.id],
            eta=scheduled_at
        )
        
        logger.info(f"AI call scheduled for application {application_id} at {scheduled_at} by {trigger_reason}")
        return {'status': 'scheduled', 'call_id': call_queue.id, 'scheduled_at': str(scheduled_at)}
        
    except Exception as e:
        logger.error(f"Failed to schedule AI call: {str(e)}")
        return {'status': 'error', 'message': str(e)}


@shared_task(name='execute_ai_call', bind=True, max_retries=3)
def execute_ai_call_task(self, call_queue_id):
    """Execute AI call with dynamic question flow"""
    from core.ai_call_models import AICallQueue
    from common.services.ai_call_eligibility import AICallEligibility
    from common.services.ai_conversation_service import AIConversationService
    from common.services.question_engine_service import QuestionEngineService
    from common.services.voice_call_service import VoiceCallService
    
    try:
        call_queue = AICallQueue.objects.get(id=call_queue_id)
        application = call_queue.application
        candidate = application.candidate
        job = application.job
        
        # Update status
        call_queue.status = 'in_progress'
        call_queue.started_at = timezone.now()
        call_queue.save()
        
        # Create session
        session = AIConversationService.create_session(call_queue)
        
        # Initialize question flow
        state = QuestionEngineService.initialize_flow(session, job)
        
        # Initiate voice call (if phone available)
        phone = getattr(candidate, 'phone', None)
        if phone:
            call_result, call_error = VoiceCallService.start_interview_call(
                candidate=candidate,
                job=job,
                language='en',
                voice_gender='female'
            )
            
            if call_error:
                logger.error(f"Voice call failed: {call_error}")
            else:
                logger.info(f"Voice call initiated: {call_result['call_sid']}")
                call_queue.error_message = f"Twilio SID: {call_result['call_sid']}"
                call_queue.save()
        
        # Dynamic question flow
        turn_number = 1
        previous_answer = None
        
        while True:
            question, category = QuestionEngineService.get_next_question(state, previous_answer)
            
            if question is None:
                break  # Interview complete
            
            # Simulate answer (replace with real Twilio response in production)
            simulated_answer = f"Simulated answer for {category} question"
            
            # Store turn
            AIConversationService.add_conversation_turn(
                session, turn_number,
                question,
                simulated_answer,
                duration=15,
                category=category,
                follow_up=False
            )
            
            # Advance state
            QuestionEngineService.advance_state(state)
            previous_answer = simulated_answer
            turn_number += 1
        
        # Save transcript
        all_turns = session.turns.all()
        transcript_text = "\n".join([f"Q: {t.question_text}\nA: {t.answer_text}" for t in all_turns])
        transcript_json = {
            "turns": [{"q": t.question_text, "a": t.answer_text, "category": t.category} for t in all_turns]
        }
        AIConversationService.save_transcript(
            session,
            transcript_text,
            transcript_json,
            confidence=0.95
        )
        
        # Calculate aggregate interview score
        from common.services.interview_scorer import InterviewScorer
        score_result, score_error = InterviewScorer.calculate_session_score(session.session_id)
        if score_error:
            logger.warning(f"Score calculation failed: {score_error}")
        else:
            logger.info(f"Interview score: {score_result['overall_score']}")
        
        # Finalize
        AIConversationService.finalize_session(
            call_queue,
            outcome='interested',
            summary='Dynamic AI interview completed successfully',
            sentiment=0.8
        )
        
        # Complete
        call_queue.status = 'completed'
        call_queue.completed_at = timezone.now()
        call_queue.call_duration = turn_number * 20
        call_queue.save()
        
        logger.info(f"AI call completed: {call_queue_id}")
        return {'status': 'completed', 'call_id': call_queue_id, 'session_id': session.session_id}
        
    except AICallQueue.DoesNotExist:
        logger.error(f"Call queue {call_queue_id} not found")
        return {'status': 'error', 'message': 'Call queue not found'}
        
    except Exception as e:
        logger.error(f"AI call failed: {str(e)}")
        
        call_queue = AICallQueue.objects.get(id=call_queue_id)
        call_queue.status = 'failed'
        call_queue.error_message = str(e)
        call_queue.retry_count += 1
        call_queue.save()
        
        if AICallEligibility.should_retry(call_queue):
            retry_delay = 60 * (2 ** call_queue.retry_count)
            logger.info(f"Retrying in {retry_delay}s (attempt {call_queue.retry_count})")
            raise self.retry(exc=e, countdown=retry_delay)
        
        return {'status': 'failed', 'message': str(e)}


@shared_task(name='process_pending_ai_calls')
def process_pending_ai_calls_task():
    """Process all pending AI calls (scheduled task)"""
    from core.ai_call_models import AICallQueue
    
    now = timezone.now()
    pending_calls = AICallQueue.objects.filter(
        status='queued',
        scheduled_at__lte=now
    )
    
    results = {'processed': 0, 'failed': 0}
    
    for call in pending_calls:
        try:
            execute_ai_call_task.delay(call.id)
            results['processed'] += 1
        except Exception as e:
            logger.error(f"Failed to trigger call {call.id}: {str(e)}")
            results['failed'] += 1
    
    return results
