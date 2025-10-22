from django.contrib import admin
from .models import Profile, ChatGroup, Message


admin.site.register(Profile)
admin.site.register(ChatGroup)
admin.site.register(Message)
