# Day 37 - Answer Evaluation & Scoring Migration

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        # Add scoring fields to AIConversationTurn
        migrations.AddField(
            model_name='aiconversationturn',
            name='answer_score',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='aiconversationturn',
            name='relevance_score',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='aiconversationturn',
            name='completeness_score',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='aiconversationturn',
            name='keyword_matches',
            field=models.JSONField(default=dict, blank=True),
        ),
        migrations.AddField(
            model_name='aiconversationturn',
            name='confidence_score',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='aiconversationturn',
            name='ai_annotations',
            field=models.JSONField(default=dict, blank=True),
        ),
        
        # Add aggregate scores to AIInterviewSession
        migrations.AddField(
            model_name='aiinterviewsession',
            name='overall_score',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='aiinterviewsession',
            name='category_scores',
            field=models.JSONField(default=dict, blank=True),
        ),
    ]
