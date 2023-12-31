# Generated by Django 4.2.5 on 2023-09-28 16:08

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    replaces = [('messages_bot', '0001_initial'), ('messages_bot', '0002_alter_message_pub_date'), ('messages_bot', '0003_alter_message_pub_date'), ('messages_bot', '0004_userinfo'), ('messages_bot', '0005_alter_userinfo_tg_chat_id'), ('messages_bot', '0006_message_user'), ('messages_bot', '0007_alter_message_user'), ('messages_bot', '0008_alter_userinfo_token')]

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=400)),
                ('pub_date', models.DateTimeField(default=django.utils.timezone.now, editable=False, verbose_name='Publication date')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.CharField(max_length=16, null=True)),
                ('tg_chat_id', models.IntegerField(blank=True, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
