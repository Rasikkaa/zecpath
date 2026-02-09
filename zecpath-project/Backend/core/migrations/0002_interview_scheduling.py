# Day 38 - Interview Scheduling Migration

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AvailabilitySlot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('employer', 'Employer'), ('candidate', 'Candidate')], max_length=20)),
                ('day_of_week', models.IntegerField()),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('is_active', models.BooleanField(default=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='availability_slots', to='core.customuser')),
            ],
        ),
        migrations.CreateModel(
            name='InterviewSchedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('interview_date', models.DateTimeField(db_index=True)),
                ('duration_minutes', models.IntegerField(default=30)),
                ('status', models.CharField(choices=[('pending', 'Pending Confirmation'), ('confirmed', 'Confirmed'), ('declined', 'Declined'), ('rescheduled', 'Rescheduled'), ('completed', 'Completed'), ('cancelled', 'Cancelled')], db_index=True, default='pending', max_length=20)),
                ('employer_confirmed', models.BooleanField(default=False)),
                ('candidate_confirmed', models.BooleanField(default=False)),
                ('meeting_link', models.URLField(blank=True)),
                ('meeting_location', models.CharField(blank=True, max_length=200)),
                ('notes', models.TextField(blank=True)),
                ('reschedule_count', models.IntegerField(default=0)),
                ('max_reschedules', models.IntegerField(default=2)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('application', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='interviews', to='core.application')),
                ('previous_schedule', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.interviewschedule')),
            ],
            options={
                'ordering': ['interview_date'],
            },
        ),
        migrations.AddIndex(
            model_name='availabilityslot',
            index=models.Index(fields=['user', 'day_of_week', 'is_active'], name='core_availa_user_id_d8e9a1_idx'),
        ),
        migrations.AddIndex(
            model_name='interviewschedule',
            index=models.Index(fields=['status', 'interview_date'], name='core_interv_status_f8c2d4_idx'),
        ),
        migrations.AddIndex(
            model_name='interviewschedule',
            index=models.Index(fields=['application', 'status'], name='core_interv_applica_a3b5e7_idx'),
        ),
    ]
