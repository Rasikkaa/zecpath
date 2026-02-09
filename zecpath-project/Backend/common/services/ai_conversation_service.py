from core.ai_call_models import AIInterviewSession, AIConversationTurn, AICallTranscript, AICallQueue
import uuid
import logging

logger = logging.getLogger(__name__)

class AIConversationService:
    
    @staticmethod
    def create_session(call_queue):
        """Create interview session for call"""
        session_id = f"AI-{call_queue.id}-{uuid.uuid4().hex[:8]}"
        session = AIInterviewSession.objects.create(
            call_queue=call_queue,
            session_id=session_id
        )
        return session
    
    @staticmethod
    def add_conversation_turn(session, turn_number, question, answer="", duration=None, category="", follow_up=False):
        """Add Q&A turn to session with optional scoring"""
        from common.services.answer_evaluator import AnswerEvaluator
        
        # Evaluate answer if provided
        scores = {}
        if answer and answer.strip():
            evaluation = AnswerEvaluator.evaluate_answer(
                question=question,
                answer=answer,
                category=category
            )
            scores = {
                'answer_score': evaluation['answer_score'],
                'relevance_score': evaluation['relevance_score'],
                'completeness_score': evaluation['completeness_score'],
                'keyword_matches': evaluation['keyword_matches'],
                'confidence_score': evaluation['confidence_score'],
                'ai_annotations': evaluation['ai_annotations']
            }
        
        turn = AIConversationTurn.objects.create(
            session=session,
            turn_number=turn_number,
            question_text=question,
            answer_text=answer,
            duration_seconds=duration,
            category=category,
            follow_up_triggered=follow_up,
            **scores
        )
        session.total_questions += 1
        if answer:
            session.total_answers += 1
        session.save()
        return turn
    
    @staticmethod
    def save_transcript(session, transcript_text, transcript_json, audio_url="", confidence=None):
        """Save full transcript"""
        transcript = AICallTranscript.objects.create(
            session=session,
            raw_audio_url=audio_url,
            transcript_text=transcript_text,
            transcript_json=transcript_json,
            confidence_score=confidence
        )
        
        # Update session
        session.full_transcript_text = transcript_text
        session.transcript_json = transcript_json
        session.save()
        
        return transcript
    
    @staticmethod
    def finalize_session(call_queue, outcome, summary="", sentiment=None):
        """Finalize call with outcome"""
        call_queue.call_outcome = outcome
        call_queue.conversation_summary = summary
        call_queue.sentiment_score = sentiment
        call_queue.save()
        
        logger.info(f"Session finalized: {call_queue.id} - Outcome: {outcome}")
