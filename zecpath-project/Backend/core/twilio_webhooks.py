"""
Twilio webhook handlers for voice call callbacks
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from common.services.voice_call_service import TwilioCallService
import logging

logger = logging.getLogger(__name__)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def twilio_callback(request):
    """Handle Twilio call initiation"""
    from twilio.twiml.voice_response import VoiceResponse
    
    response = VoiceResponse()
    response.say(
        "Hello, this is an automated interview call from ZecPath. "
        "Please answer the following questions.",
        voice='Polly.Joanna'
    )
    
    # Redirect to first question
    response.redirect('/api/ai-calls/twilio-question/1/')
    
    return HttpResponse(str(response), content_type='text/xml')


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def twilio_question(request, question_num):
    """Ask interview question"""
    from twilio.twiml.voice_response import VoiceResponse, Gather
    
    # Get questions from session (simplified)
    questions = [
        "Tell me about your experience?",
        "What are your key strengths?",
        "When can you start?"
    ]
    
    response = VoiceResponse()
    
    if question_num <= len(questions):
        gather = Gather(
            input='speech',
            action=f'/api/ai-calls/twilio-response/{question_num}/',
            method='POST',
            speech_timeout='auto'
        )
        gather.say(questions[question_num - 1], voice='Polly.Joanna')
        response.append(gather)
    else:
        response.say("Thank you for your time. Goodbye!", voice='Polly.Joanna')
        response.hangup()
    
    return HttpResponse(str(response), content_type='text/xml')


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def twilio_response(request, question_num):
    """Process candidate response"""
    from twilio.twiml.voice_response import VoiceResponse
    
    speech_result = request.POST.get('SpeechResult', '')
    logger.info(f"Q{question_num} Answer: {speech_result}")
    
    # Store response (implement storage logic)
    
    response = VoiceResponse()
    response.redirect(f'/api/ai-calls/twilio-question/{question_num + 1}/')
    
    return HttpResponse(str(response), content_type='text/xml')


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def twilio_status_callback(request):
    """Handle call status updates"""
    call_sid = request.POST.get('CallSid')
    call_status = request.POST.get('CallStatus')
    
    logger.info(f"Call {call_sid} status: {call_status}")
    
    # Update AICallQueue status based on call_sid
    
    return Response({'status': 'received'})
