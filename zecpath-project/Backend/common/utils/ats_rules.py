from django.core.exceptions import ValidationError

class ATSWorkflowRules:
    """Business rules for ATS status transitions"""
    
    VALID_TRANSITIONS = {
        'pending': ['shortlisted', 'rejected'],
        'shortlisted': ['interview_scheduled', 'rejected'],
        'interview_scheduled': ['reviewed', 'rejected'],
        'reviewed': ['accepted', 'rejected', 'selected'],
        'accepted': ['selected'],
        'rejected': [],  # Terminal state
        'selected': [],  # Terminal state
    }
    
    LOCKED_STAGES = ['rejected', 'selected']
    
    @classmethod
    def validate_transition(cls, from_status, to_status):
        """Validate if status transition is allowed"""
        if from_status in cls.LOCKED_STAGES:
            raise ValidationError(f"Cannot change status from {from_status}")
        
        if to_status not in cls.VALID_TRANSITIONS.get(from_status, []):
            raise ValidationError(f"Invalid transition from {from_status} to {to_status}")
        
        return True
    
    @classmethod
    def get_allowed_transitions(cls, current_status):
        """Get list of allowed next statuses"""
        return cls.VALID_TRANSITIONS.get(current_status, [])