# Generated migration for ATS scoring fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0022_auditlog'),
    ]

    operations = [
        migrations.AddField(
            model_name='application',
            name='match_score',
            field=models.IntegerField(db_index=True, default=0),
        ),
        migrations.AddField(
            model_name='application',
            name='match_breakdown',
            field=models.JSONField(blank=True, default=dict),
        ),
    ]
