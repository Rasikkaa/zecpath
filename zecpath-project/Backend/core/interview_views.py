"""
Interview Scheduling API Views
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from core.permissions import IsEmployer, IsCandidate, IsAdmin
from core.models import Application
from core.interview_models import InterviewSchedule, AvailabilitySlot
from common.services.interview_scheduler import InterviewScheduler
from common.services.email_service import EmailService
from common.utils.pagination import paginate_queryset
from django.utils import timezone


class AvailabilitySlotAPI(APIView):
    permission_classes = [IsEmployer | IsCandidate]
    
    def get(self, request):
        """Get user's availability slots"""
        slots = AvailabilitySlot.objects.filter(user=request.user, is_active=True).order_by('day_of_week', 'start_time')
        
        data = [{
            'id': s.id,
            'day_of_week': s.day_of_week,
            'day_name': s.get_day_display(),
            'start_time': s.start_time.strftime('%H:%M'),
            'end_time': s.end_time.strftime('%H:%M')
        } for s in slots]
        
        return Response({'results': data})
    
    def post(self, request):
        """Set availability slots"""
        slots_data = request.data.get('slots', [])
        
        # Clear existing
        AvailabilitySlot.objects.filter(user=request.user).delete()
        
        # Create new
        for slot in slots_data:
            AvailabilitySlot.objects.create(
                user=request.user,
                role=request.user.role,
                day_of_week=slot['day_of_week'],
                start_time=slot['start_time'],
                end_time=slot['end_time']
            )
        
        return Response({'message': 'Availability updated'}, status=status.HTTP_201_CREATED)


class InterviewScheduleAPI(APIView):
    permission_classes = [IsEmployer | IsAdmin]
    
    def post(self, request, application_id):
        """Schedule interview for application"""
        try:
            if request.user.role == 'employer':
                application = Application.objects.get(id=application_id, job__employer__user=request.user)
            else:
                application = Application.objects.get(id=application_id)
            
            interview_date = request.data.get('interview_date')
            auto_schedule = request.data.get('auto_schedule', False)
            
            if interview_date:
                interview_date = timezone.datetime.fromisoformat(interview_date.replace('Z', '+00:00'))
            
            schedule, error = InterviewScheduler.schedule_interview(application, interview_date, auto_schedule)
            
            if error:
                return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)
            
            # Send notifications
            EmailService.send_interview_scheduled(schedule)
            
            # Create reminders
            from common.tasks_reminders import create_reminders_for_new_interview
            create_reminders_for_new_interview.delay(schedule.id)
            
            return Response({
                'message': 'Interview scheduled',
                'schedule_id': schedule.id,
                'interview_date': schedule.interview_date,
                'status': schedule.status
            }, status=status.HTTP_201_CREATED)
            
        except Application.DoesNotExist:
            return Response({'error': 'Application not found'}, status=status.HTTP_404_NOT_FOUND)


class AvailableSlotsAPI(APIView):
    permission_classes = [IsEmployer | IsAdmin]
    
    def get(self, request, application_id):
        """Get available time slots for interview"""
        try:
            if request.user.role == 'employer':
                application = Application.objects.get(id=application_id, job__employer__user=request.user)
            else:
                application = Application.objects.get(id=application_id)
            
            days_ahead = int(request.GET.get('days', 7))
            max_slots = int(request.GET.get('max_slots', 10))
            
            slots = InterviewScheduler.find_available_slots(application, days_ahead, max_slots)
            
            return Response({
                'application_id': application_id,
                'available_slots': [s.isoformat() for s in slots],
                'count': len(slots)
            })
            
        except Application.DoesNotExist:
            return Response({'error': 'Application not found'}, status=status.HTTP_404_NOT_FOUND)


class InterviewConfirmAPI(APIView):
    permission_classes = [IsEmployer | IsCandidate]
    
    def post(self, request, schedule_id):
        """Confirm interview"""
        try:
            schedule = InterviewSchedule.objects.get(id=schedule_id)
            
            # Check permission
            if request.user.role == 'employer':
                if schedule.application.job.employer.user != request.user:
                    return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
            elif request.user.role == 'candidate':
                if schedule.application.candidate.user != request.user:
                    return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
            
            schedule = InterviewScheduler.confirm_interview(schedule, request.user.role)
            
            # Send confirmation email
            if schedule.is_confirmed():
                EmailService.send_interview_confirmed(schedule)
            
            return Response({
                'message': 'Interview confirmed',
                'status': schedule.status,
                'employer_confirmed': schedule.employer_confirmed,
                'candidate_confirmed': schedule.candidate_confirmed
            })
            
        except InterviewSchedule.DoesNotExist:
            return Response({'error': 'Schedule not found'}, status=status.HTTP_404_NOT_FOUND)


class InterviewDeclineAPI(APIView):
    permission_classes = [IsEmployer | IsCandidate]
    
    def post(self, request, schedule_id):
        """Decline interview"""
        try:
            schedule = InterviewSchedule.objects.get(id=schedule_id)
            
            # Check permission
            if request.user.role == 'employer':
                if schedule.application.job.employer.user != request.user:
                    return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
            elif request.user.role == 'candidate':
                if schedule.application.candidate.user != request.user:
                    return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
            
            schedule = InterviewScheduler.decline_interview(schedule, request.user.role)
            
            return Response({'message': 'Interview declined'})
            
        except InterviewSchedule.DoesNotExist:
            return Response({'error': 'Schedule not found'}, status=status.HTTP_404_NOT_FOUND)


class InterviewRescheduleAPI(APIView):
    permission_classes = [IsEmployer | IsCandidate]
    
    def post(self, request, schedule_id):
        """Reschedule interview"""
        try:
            schedule = InterviewSchedule.objects.get(id=schedule_id)
            
            # Check permission
            if request.user.role == 'employer':
                if schedule.application.job.employer.user != request.user:
                    return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
            elif request.user.role == 'candidate':
                if schedule.application.candidate.user != request.user:
                    return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
            
            new_date = request.data.get('new_date')
            if not new_date:
                return Response({'error': 'New date required'}, status=status.HTTP_400_BAD_REQUEST)
            
            new_date = timezone.datetime.fromisoformat(new_date.replace('Z', '+00:00'))
            
            new_schedule, error = InterviewScheduler.reschedule_interview(schedule, new_date)
            
            if error:
                return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)
            
            # Send notification
            EmailService.send_interview_rescheduled(new_schedule)
            
            # Cancel old reminders and create new ones
            from common.services.reminder_service import ReminderService
            from common.tasks_reminders import create_reminders_for_new_interview
            ReminderService.cancel_reminders(schedule)
            create_reminders_for_new_interview.delay(new_schedule.id)
            
            return Response({
                'message': 'Interview rescheduled',
                'new_schedule_id': new_schedule.id,
                'new_date': new_schedule.interview_date
            })
            
        except InterviewSchedule.DoesNotExist:
            return Response({'error': 'Schedule not found'}, status=status.HTTP_404_NOT_FOUND)


class InterviewListAPI(APIView):
    permission_classes = [IsEmployer | IsCandidate | IsAdmin]
    
    def get(self, request):
        """List interviews"""
        if request.user.role == 'employer':
            schedules = InterviewSchedule.objects.filter(
                application__job__employer__user=request.user
            ).select_related('application__candidate__user', 'application__job')
        elif request.user.role == 'candidate':
            schedules = InterviewSchedule.objects.filter(
                application__candidate__user=request.user
            ).select_related('application__job__employer__user')
        else:
            schedules = InterviewSchedule.objects.all().select_related(
                'application__candidate__user', 'application__job__employer__user'
            )
        
        # Filter by status
        status_filter = request.GET.get('status')
        if status_filter:
            schedules = schedules.filter(status=status_filter)
        
        schedules = schedules.order_by('-interview_date')
        
        result = paginate_queryset(schedules, request)
        
        data = [{
            'id': s.id,
            'application_id': s.application.id,
            'candidate': s.application.candidate.user.email,
            'job_title': s.application.job.title,
            'interview_date': s.interview_date,
            'duration_minutes': s.duration_minutes,
            'status': s.status,
            'employer_confirmed': s.employer_confirmed,
            'candidate_confirmed': s.candidate_confirmed,
            'meeting_link': s.meeting_link,
            'meeting_location': s.meeting_location
        } for s in result['page_obj']]
        
        result['results'] = data
        del result['page_obj']
        
        return Response(result)
