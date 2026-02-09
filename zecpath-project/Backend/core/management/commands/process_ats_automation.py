from django.core.management.base import BaseCommand
from common.services.automation_service import AutomationService

class Command(BaseCommand):
    help = 'Process ATS automation for all jobs with automation enabled'
    
    def handle(self, *args, **options):
        self.stdout.write('Starting ATS automation processing...')
        
        results = AutomationService.bulk_process_applications()
        
        self.stdout.write(self.style.SUCCESS(
            f"Processed {results['jobs_processed']} jobs, "
            f"{results['total_applications']} applications: "
            f"{results['shortlisted']} shortlisted, "
            f"{results['rejected']} rejected"
        ))
