from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import os


def profile_picture_path(instance, filename):
    ext = filename.split('.')[-1]
    return os.path.join('profiles', f'{instance.user.username}.{ext}')

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=150, blank=True)
    bio = models.TextField(blank=True)
    picture = models.ImageField(upload_to=profile_picture_path, blank=True, null=True)

    def display_name(self):
        return self.name if self.name else self.user.username

    def __str__(self):
        return f'Profile({self.user.username})'

class ChatGroup(models.Model):
    name = models.CharField(max_length=150)
    members = models.ManyToManyField(
        User,
        related_name='chat_groups',
        related_query_name='chat_group'
    )
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    content = models.TextField(blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    room_name = models.CharField(max_length=255)
    is_group = models.BooleanField(default=False)

    class Meta:
        ordering = ('timestamp',)
