from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import User
from django.dispatch import receiver
import secrets


@receiver(models.signals.post_save, sender=User)
def create_userinfo(sender, instance, created, **kwargs):
    if created:
        user_info = UserInfo(user=instance)
        user_info.save()


class Message(models.Model):
    text = models.CharField(max_length=400)
    pub_date = models.DateTimeField(verbose_name="Publication date", default=now, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class UserInfo(models.Model):
    token = models.CharField(max_length=16, null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    tg_chat_id = models.IntegerField(null=True, blank=True)

    def generate_token(self):
        self.token = secrets.token_hex(16)
        self.save()

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = self.generate_token()

        return super().save(*args, **kwargs)
