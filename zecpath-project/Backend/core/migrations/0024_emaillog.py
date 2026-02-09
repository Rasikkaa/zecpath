# Generated migration for EmailLog model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0023_application_match_score_match_breakdown'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recipient', models.EmailField(db_index=True, max_length=254)),
                ('subject', models.CharField(max_length=255)),
                ('template_name', models.CharField(max_length=100)),
                ('context_data', models.JSONField(default=dict)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('sent', 'Sent'), ('failed', 'Failed')], db_index=True, default='pending', max_length=20)),
                ('error_message', models.TextField(blank=True)),
                ('sent_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('retry_count', models.IntegerField(default=0)),
            ],
            options={
                'ordering': ['-created_at'],
                'indexes': [
                    models.Index(fields=['status', 'created_at'], name='core_emaill_status_idx'),
                    models.Index(fields=['recipient', 'created_at'], name='core_emaill_recipient_idx'),
                ],
            },
        ),
    ]
