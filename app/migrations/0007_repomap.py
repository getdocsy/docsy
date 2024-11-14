# Generated by Django 5.1.3 on 2024-11-14 16:29

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_remove_analysis_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='RepoMap',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('result', models.JSONField(default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_for_commit_sha', models.CharField(max_length=255)),
                ('repo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.repo')),
            ],
        ),
    ]
