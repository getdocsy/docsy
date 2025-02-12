# Generated by Django 5.1.3 on 2024-11-12 14:00

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0002_repo_is_public_analysis"),
    ]

    operations = [
        migrations.RenameField(
            model_name="repo",
            old_name="github_full_name",
            new_name="nfkc_clone_url",
        ),
        migrations.AddField(
            model_name="analysis",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="repo",
            name="nfkc_github_full_name",
            field=models.CharField(default="abc", max_length=255),
            preserve_default=False,
        ),
    ]
