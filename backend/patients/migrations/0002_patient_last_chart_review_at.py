from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("patients", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="patient",
            name="last_chart_review_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
