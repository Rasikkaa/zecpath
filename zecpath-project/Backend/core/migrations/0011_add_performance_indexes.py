from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_alter_application_id_alter_candidate_id_and_more'),
    ]

    operations = [
        # Add indexes to CustomUser
        migrations.AlterField(
            model_name='customuser',
            name='role',
            field=models.CharField(choices=[('admin', 'Admin'), ('employer', 'Employer'), ('candidate', 'Candidate')], db_index=True, max_length=20),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='is_verified',
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
        
        # Add indexes to Job
        migrations.AlterField(
            model_name='job',
            name='title',
            field=models.CharField(db_index=True, max_length=200),
        ),
        migrations.AlterField(
            model_name='job',
            name='location',
            field=models.CharField(db_index=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='job',
            name='status',
            field=models.CharField(choices=[('draft', 'Draft'), ('published', 'Published'), ('closed', 'Closed')], db_index=True, default='published', max_length=20),
        ),
        migrations.AlterField(
            model_name='job',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
        
        # Add indexes to Application
        migrations.AlterField(
            model_name='application',
            name='status',
            field=models.CharField(db_index=True, default='pending', max_length=50),
        ),
        migrations.AlterField(
            model_name='application',
            name='applied_at',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
        
        # Add indexes to Candidate
        migrations.AlterField(
            model_name='candidate',
            name='expected_salary',
            field=models.IntegerField(blank=True, db_index=True, null=True),
        ),
        migrations.AlterField(
            model_name='candidate',
            name='experience_years',
            field=models.IntegerField(db_index=True, default=0),
        ),
        
        # Add indexes to Employer
        migrations.AlterField(
            model_name='employer',
            name='company_name',
            field=models.CharField(blank=True, db_index=True, max_length=200),
        ),
        migrations.AlterField(
            model_name='employer',
            name='domain',
            field=models.CharField(blank=True, db_index=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='employer',
            name='verification',
            field=models.BooleanField(db_index=True, default=False),
        ),
        
        # Add composite indexes
        migrations.AddIndex(
            model_name='job',
            index=models.Index(fields=['status', 'created_at'], name='core_job_status_created_idx'),
        ),
        migrations.AddIndex(
            model_name='job',
            index=models.Index(fields=['location', 'status'], name='core_job_location_status_idx'),
        ),
        migrations.AddIndex(
            model_name='job',
            index=models.Index(fields=['title', 'status'], name='core_job_title_status_idx'),
        ),
        migrations.AddIndex(
            model_name='application',
            index=models.Index(fields=['status', 'applied_at'], name='core_application_status_applied_idx'),
        ),
        migrations.AddIndex(
            model_name='application',
            index=models.Index(fields=['candidate', 'applied_at'], name='core_application_candidate_applied_idx'),
        ),
        migrations.AddIndex(
            model_name='application',
            index=models.Index(fields=['job', 'applied_at'], name='core_application_job_applied_idx'),
        ),
        migrations.AddIndex(
            model_name='candidate',
            index=models.Index(fields=['experience_years', 'expected_salary'], name='core_candidate_exp_salary_idx'),
        ),
        
        # Add unique constraint
        migrations.AlterUniqueTogether(
            name='application',
            unique_together={('candidate', 'job')},
        ),
    ]