# Generated by Django 3.0.4 on 2020-05-25 14:29

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Prompt',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('body', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('text', models.CharField(max_length=100)),
                ('human', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='EvaluationText',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('body', models.TextField()),
                ('boundary', models.IntegerField()),
                ('prompt', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='core.Prompt')),
            ],
        ),
        migrations.CreateModel(
            name='Annotation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now=True, null=True)),
                ('boundary', models.IntegerField()),
                ('revision', models.TextField()),
                ('annotator', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
                ('tags', models.ManyToManyField(related_name='annotation_tags', to='core.Tag')),
                ('text', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='core.EvaluationText')),
            ],
        ),
    ]
