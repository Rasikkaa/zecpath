# Generated migration for Day 39 - Interview Reminders

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_interview_scheduling'),
    ]

    operations = [
        migrations.CreateModel(
            name='InterviewReminder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reminder_type', models.CharField(choices=[('24h', '24 Hours Before'), ('2h', '2 Hours Before'), ('30min', '30 Minutes Before')], max_length=10)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('sent', 'Sent'), ('failed', 'Failed')], db_index=True, default='pending', max_length=20)),
                ('scheduled_at', models.DateTimeField(db_index=True)),
                ('sent_at', models.DateTimeField(blank=True, null=True)),
                ('error_message', models.TextField(blank=True)),
                ('retry_count', models.IntegerField(default=0)),
                ('max_retries', models.IntegerField(default=3)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('schedule', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reminders', to='core.interviewschedule')),
            ],
            options={
                'ordering': ['scheduled_at'],
                'indexes': [
                    models.Index(fields=['status', 'scheduled_at'], name='core_interv_status_idx'),
                ],
                'unique_together': {('schedule', 'reminder_type')},
            },
        ),
    ]
