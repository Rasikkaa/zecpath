# Generated migration for automation fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employers', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='auto_shortlist_enabled',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='job',
            name='auto_shortlist_threshold',
            field=models.IntegerField(default=80),
        ),
        migrations.AddField(
            model_name='job',
            name='auto_reject_threshold',
            field=models.IntegerField(default=30),
        ),
    ]
