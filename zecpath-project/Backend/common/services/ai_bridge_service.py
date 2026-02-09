"""
AI Bridge Service - Central integration point for LLM, STT, TTS
"""
import os
import logging
import time
from django.conf import settings

logger = logging.getLogger(__name__)


class LLMService:
    """LLM API wrapper (OpenAI/Anthropic)"""
    
    MAX_RETRIES = 3
    RETRY_DELAY = 2
    
    @staticmethod
    def generate_interview_questions(job_title, skills, num_questions=3):
        """Generate interview questions using LLM"""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            
            prompt = f"""Generate {num_questions} interview questions for a {job_title} position.
Required skills: {', '.join(skills) if isinstance(skills, list) else skills}

Return only the questions, numbered 1-{num_questions}."""

            response = client.chat.completions.create(
                model=os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo'),
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.7
            )
            
            questions = response.choices[0].message.content.strip().split('\n')
            return [q.strip() for q in questions if q.strip()], None
            
        except ImportError:
            logger.warning("OpenAI not installed, using fallback questions")
            return LLMService._fallback_questions(job_title), None
        except Exception as e:
            logger.error(f"LLM error: {str(e)}")
            return LLMService._fallback_questions(job_title), str(e)
    
    @staticmethod
    def _fallback_questions(job_title):
        """Fallback questions if API fails"""
        return [
            f"Tell me about your experience with {job_title} roles?",
            "What are your key technical strengths?",
            "When can you start if selected?"
        ]
    
    @staticmethod
    def analyze_response(question, answer):
        """Analyze candidate response (optional)"""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            
            prompt = f"Question: {question}\nAnswer: {answer}\n\nRate this answer 1-10 and explain briefly."
            
            response = client.chat.completions.create(
                model=os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo'),
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100
            )
            
            return response.choices[0].message.content.strip(), None
        except Exception as e:
            return None, str(e)


class STTService:
    """Speech-to-Text service"""
    
    @staticmethod
    def transcribe_audio(audio_url, language='en'):
        """Convert speech to text"""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            
            # Download audio file
            import requests
            audio_data = requests.get(audio_url).content
            
            # Save temporarily
            temp_path = f"/tmp/audio_{int(time.time())}.mp3"
            with open(temp_path, 'wb') as f:
                f.write(audio_data)
            
            # Transcribe
            with open(temp_path, 'rb') as audio_file:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language=language
                )
            
            os.remove(temp_path)
            return transcript.text, None
            
        except Exception as e:
            logger.error(f"STT error: {str(e)}")
            return None, str(e)


class TTSService:
    """Text-to-Speech service"""
    
    VOICES = {
        'en': {'male': 'alloy', 'female': 'nova'},
        'es': {'male': 'onyx', 'female': 'shimmer'},
    }
    
    @staticmethod
    def synthesize_speech(text, language='en', gender='female'):
        """Convert text to speech"""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            
            voice = TTSService.VOICES.get(language, TTSService.VOICES['en']).get(gender, 'nova')
            
            response = client.audio.speech.create(
                model="tts-1",
                voice=voice,
                input=text
            )
            
            return response.content, None
            
        except Exception as e:
            logger.error(f"TTS error: {str(e)}")
            return None, str(e)


class AIBridgeService:
    """Central AI service coordinator"""
    
    @staticmethod
    def conduct_interview(job_title, skills, language='en'):
        """Full interview flow"""
        # Generate questions
        questions, error = LLMService.generate_interview_questions(job_title, skills)
        if error:
            logger.error(f"Question generation failed: {error}")
        
        return {
            'questions': questions,
            'language': language,
            'status': 'ready' if not error else 'fallback'
        }
    
    @staticmethod
    def process_voice_response(audio_url, language='en'):
        """Process voice answer"""
        transcript, error = STTService.transcribe_audio(audio_url, language)
        if error:
            return None, error
        
        return {
            'transcript': transcript,
            'confidence': 0.95  # Placeholder
        }, None
    
    @staticmethod
    def with_retry(func, *args, max_retries=3, **kwargs):
        """Retry wrapper for API calls"""
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                logger.warning(f"Retry {attempt + 1}/{max_retries}: {str(e)}")
                time.sleep(2 ** attempt)
