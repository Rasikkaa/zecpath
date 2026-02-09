# Generated manually for Day 33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('candidates', '0002_savedjob'),
    ]

    operations = [
        migrations.AddField(
            model_name='candidate',
            name='is_available_for_call',
            field=models.BooleanField(default=True, db_index=True),
        ),
    ]
