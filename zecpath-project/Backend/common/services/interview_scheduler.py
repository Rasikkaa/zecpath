"""
Interview Scheduling Service - Auto-schedule interviews
"""
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Q


class InterviewScheduler:
    """Auto-schedule interviews with conflict resolution"""
    
    DEFAULT_DURATION = 30  # minutes
    BUFFER_TIME = 15  # minutes between interviews
    WORKING_HOURS = (9, 18)  # 9 AM - 6 PM
    
    @staticmethod
    def find_available_slots(application, days_ahead=7, max_slots=10):
        """Find available time slots for interview"""
        from core.interview_models import AvailabilitySlot, InterviewSchedule
        
        employer = application.job.employer.user
        candidate = application.candidate.user
        
        # Get availability
        employer_slots = AvailabilitySlot.objects.filter(user=employer, is_active=True)
        candidate_slots = AvailabilitySlot.objects.filter(user=candidate, is_active=True)
        
        # If no availability set, use default working hours
        if not employer_slots.exists():
            employer_slots = InterviewScheduler._get_default_slots(employer)
        if not candidate_slots.exists():
            candidate_slots = InterviewScheduler._get_default_slots(candidate)
        
        available_slots = []
        start_date = timezone.now().date()
        
        for day_offset in range(days_ahead):
            check_date = start_date + timedelta(days=day_offset)
            day_of_week = check_date.weekday()
            
            # Get slots for this day
            emp_day_slots = [s for s in employer_slots if s.day_of_week == day_of_week]
            cand_day_slots = [s for s in candidate_slots if s.day_of_week == day_of_week]
            
            if not emp_day_slots or not cand_day_slots:
                continue
            
            # Find overlapping time slots
            for emp_slot in emp_day_slots:
                for cand_slot in cand_day_slots:
                    overlap_start = max(emp_slot.start_time, cand_slot.start_time)
                    overlap_end = min(emp_slot.end_time, cand_slot.end_time)
                    
                    if overlap_start < overlap_end:
                        # Generate time slots
                        current_time = datetime.combine(check_date, overlap_start)
                        end_time = datetime.combine(check_date, overlap_end)
                        
                        while current_time + timedelta(minutes=InterviewScheduler.DEFAULT_DURATION) <= end_time:
                            slot_datetime = timezone.make_aware(current_time)
                            
                            # Check conflicts
                            if not InterviewScheduler._has_conflict(employer, candidate, slot_datetime):
                                available_slots.append(slot_datetime)
                                
                                if len(available_slots) >= max_slots:
                                    return available_slots
                            
                            current_time += timedelta(minutes=InterviewScheduler.DEFAULT_DURATION + InterviewScheduler.BUFFER_TIME)
        
        return available_slots
    
    @staticmethod
    def _get_default_slots(user):
        """Generate default working hours slots"""
        from core.interview_models import AvailabilitySlot
        
        slots = []
        for day in range(5):  # Monday to Friday
            slot = AvailabilitySlot(
                user=user,
                role=user.role,
                day_of_week=day,
                start_time=datetime.strptime('09:00', '%H:%M').time(),
                end_time=datetime.strptime('18:00', '%H:%M').time(),
                is_active=True
            )
            slots.append(slot)
        return slots
    
    @staticmethod
    def _has_conflict(employer, candidate, slot_datetime):
        """Check if time slot has conflicts"""
        from core.interview_models import InterviewSchedule
        
        slot_end = slot_datetime + timedelta(minutes=InterviewScheduler.DEFAULT_DURATION)
        
        # Check employer conflicts
        employer_conflicts = InterviewSchedule.objects.filter(
            application__job__employer__user=employer,
            status__in=['pending', 'confirmed'],
            interview_date__lt=slot_end,
            interview_date__gte=slot_datetime - timedelta(minutes=InterviewScheduler.DEFAULT_DURATION)
        ).exists()
        
        # Check candidate conflicts
        candidate_conflicts = InterviewSchedule.objects.filter(
            application__candidate__user=candidate,
            status__in=['pending', 'confirmed'],
            interview_date__lt=slot_end,
            interview_date__gte=slot_datetime - timedelta(minutes=InterviewScheduler.DEFAULT_DURATION)
        ).exists()
        
        return employer_conflicts or candidate_conflicts
    
    @staticmethod
    def schedule_interview(application, interview_date=None, auto_schedule=True):
        """Schedule interview automatically or manually"""
        from core.interview_models import InterviewSchedule
        
        if auto_schedule and not interview_date:
            # Find first available slot
            slots = InterviewScheduler.find_available_slots(application, max_slots=1)
            if not slots:
                return None, "No available slots found"
            interview_date = slots[0]
        
        if not interview_date:
            return None, "Interview date required"
        
        # Validate date
        if interview_date < timezone.now():
            return None, "Interview date must be in the future"
        
        # Create schedule
        schedule = InterviewSchedule.objects.create(
            application=application,
            interview_date=interview_date,
            duration_minutes=InterviewScheduler.DEFAULT_DURATION,
            status='pending'
        )
        
        # Update application status
        application.status = 'interview_scheduled'
        application.save()
        
        return schedule, None
    
    @staticmethod
    def reschedule_interview(schedule, new_date):
        """Reschedule existing interview"""
        from core.interview_models import InterviewSchedule
        
        if not schedule.can_reschedule():
            return None, "Maximum reschedule limit reached"
        
        if new_date < timezone.now():
            return None, "New date must be in the future"
        
        # Check conflicts
        employer = schedule.application.job.employer.user
        candidate = schedule.application.candidate.user
        
        if InterviewScheduler._has_conflict(employer, candidate, new_date):
            return None, "Time slot has conflicts"
        
        # Create new schedule
        new_schedule = InterviewSchedule.objects.create(
            application=schedule.application,
            interview_date=new_date,
            duration_minutes=schedule.duration_minutes,
            status='pending',
            reschedule_count=schedule.reschedule_count + 1,
            previous_schedule=schedule
        )
        
        # Mark old as rescheduled
        schedule.status = 'rescheduled'
        schedule.save()
        
        return new_schedule, None
    
    @staticmethod
    def confirm_interview(schedule, user_role):
        """Confirm interview by employer or candidate"""
        if user_role == 'employer':
            schedule.employer_confirmed = True
        elif user_role == 'candidate':
            schedule.candidate_confirmed = True
        
        # If both confirmed, update status
        if schedule.is_confirmed():
            schedule.status = 'confirmed'
        
        schedule.save()
        return schedule
    
    @staticmethod
    def decline_interview(schedule, user_role):
        """Decline interview"""
        schedule.status = 'declined'
        schedule.save()
        return schedule
