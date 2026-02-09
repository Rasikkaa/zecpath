"""
Voice Call Service - Twilio integration for outbound calls
"""
import os
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


class TwilioCallService:
    """Twilio voice call integration"""
    
    @staticmethod
    def initiate_call(to_phone, callback_url, language='en'):
        """Start outbound call"""
        try:
            from twilio.rest import Client
            
            account_sid = os.getenv('TWILIO_ACCOUNT_SID')
            auth_token = os.getenv('TWILIO_AUTH_TOKEN')
            from_phone = os.getenv('TWILIO_PHONE_NUMBER')
            
            if not all([account_sid, auth_token, from_phone]):
                return None, "Twilio credentials not configured"
            
            client = Client(account_sid, auth_token)
            
            call = client.calls.create(
                to=to_phone,
                from_=from_phone,
                url=callback_url,
                method='POST',
                status_callback=callback_url + '/status',
                status_callback_event=['initiated', 'ringing', 'answered', 'completed']
            )
            
            return {
                'call_sid': call.sid,
                'status': call.status,
                'to': to_phone
            }, None
            
        except ImportError:
            logger.error("Twilio not installed: pip install twilio")
            return None, "Twilio library not installed"
        except Exception as e:
            logger.error(f"Twilio call failed: {str(e)}")
            return None, str(e)
    
    @staticmethod
    def get_call_status(call_sid):
        """Check call status"""
        try:
            from twilio.rest import Client
            
            client = Client(
                os.getenv('TWILIO_ACCOUNT_SID'),
                os.getenv('TWILIO_AUTH_TOKEN')
            )
            
            call = client.calls(call_sid).fetch()
            return {
                'status': call.status,
                'duration': call.duration,
                'price': call.price
            }, None
            
        except Exception as e:
            return None, str(e)
    
    @staticmethod
    def generate_twiml_response(text, language='en', voice='female'):
        """Generate TwiML for voice response"""
        from twilio.twiml.voice_response import VoiceResponse, Gather
        
        response = VoiceResponse()
        
        # Select voice
        voice_map = {
            'en': {'male': 'Polly.Matthew', 'female': 'Polly.Joanna'},
            'es': {'male': 'Polly.Miguel', 'female': 'Polly.Lupe'}
        }
        
        selected_voice = voice_map.get(language, voice_map['en']).get(voice, 'Polly.Joanna')
        
        # Gather response
        gather = Gather(
            input='speech',
            action='/api/ai-calls/voice-response/',
            method='POST',
            language=language,
            speech_timeout='auto'
        )
        gather.say(text, voice=selected_voice, language=language)
        response.append(gather)
        
        # Fallback
        response.say("We didn't receive any input. Goodbye!", voice=selected_voice)
        
        return str(response)


class VoiceCallService:
    """High-level voice call orchestration"""
    
    SUPPORTED_LANGUAGES = ['en', 'es', 'fr', 'de']
    
    @staticmethod
    def start_interview_call(candidate, job, language='en', voice_gender='female'):
        """Start AI interview call"""
        
        # Validate language
        if language not in VoiceCallService.SUPPORTED_LANGUAGES:
            language = 'en'
        
        # Get candidate phone
        phone = getattr(candidate, 'phone', None)
        if not phone:
            return None, "Candidate phone number not found"
        
        # Generate callback URL
        callback_url = f"{settings.BASE_URL}/api/ai-calls/twilio-callback/"
        
        # Initiate call
        result, error = TwilioCallService.initiate_call(
            to_phone=phone,
            callback_url=callback_url,
            language=language
        )
        
        if error:
            return None, error
        
        return {
            'call_sid': result['call_sid'],
            'status': result['status'],
            'language': language,
            'voice_gender': voice_gender
        }, None
    
    @staticmethod
    def select_voice(language, gender='female'):
        """Select appropriate voice for language/gender"""
        voices = {
            'en': {'male': 'en-US-Male', 'female': 'en-US-Female'},
            'es': {'male': 'es-ES-Male', 'female': 'es-ES-Female'},
            'fr': {'male': 'fr-FR-Male', 'female': 'fr-FR-Female'},
            'de': {'male': 'de-DE-Male', 'female': 'de-DE-Female'}
        }
        
        return voices.get(language, voices['en']).get(gender, 'en-US-Female')
