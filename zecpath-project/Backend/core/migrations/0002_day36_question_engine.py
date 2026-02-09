# Generated for Day 36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0027_aicallqueue_call_outcome_and_more'),
        ('employers', '0001_initial'),
    ]

    operations = [
        # Add category and follow_up_triggered to AIConversationTurn
        migrations.AddField(
            model_name='aiconversationturn',
            name='category',
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name='aiconversationturn',
            name='follow_up_triggered',
            field=models.BooleanField(default=False),
        ),
        
        # Create QuestionTemplate
        migrations.CreateModel(
            name='QuestionTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(choices=[('introduction', 'Introduction'), ('experience', 'Experience'), ('skills', 'Skills'), ('availability', 'Availability'), ('salary', 'Salary')], db_index=True, max_length=20)),
                ('question_text', models.TextField()),
                ('role', models.CharField(blank=True, max_length=50)),
                ('condition', models.JSONField(blank=True, default=dict)),
                ('follow_up_trigger', models.JSONField(blank=True, default=dict)),
                ('order', models.IntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ['category', 'order'],
            },
        ),
        
        # Create QuestionFlow
        migrations.CreateModel(
            name='QuestionFlow',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.IntegerField(default=0)),
                ('is_required', models.BooleanField(default=True)),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='question_flows', to='employers.job')),
                ('template', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.questiontemplate')),
            ],
            options={
                'ordering': ['order'],
                'unique_together': {('job', 'template', 'order')},
            },
        ),
        
        # Create InterviewState
        migrations.CreateModel(
            name='InterviewState',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('current_question_index', models.IntegerField(default=0)),
                ('context', models.JSONField(default=dict)),
                ('completed_categories', models.JSONField(default=list)),
                ('next_question_id', models.IntegerField(blank=True, null=True)),
                ('session', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='state', to='core.aiinterviewsession')),
            ],
        ),
    ]
