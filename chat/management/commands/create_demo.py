from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from chat.models import Profile, Message, ChatGroup
from django.utils import timezone

class Command(BaseCommand):
    def handle(self, *args, **options):
        demo_users = [
            ('alice','alice@example.com','password123','Alice','Hey I am Alice'),
            ('bob','bob@example.com','password123','Bob','I like photography'),
            ('carol','carol@example.com','password123','Carol','Designer'),
            ('dave','dave@example.com','password123','Dave','Coffee lover'),
        ]
        created = []
        for uname,email,pw,name,bio in demo_users:
            u, created_flag = User.objects.get_or_create(username=uname, defaults={'email':email})
            if created_flag:
                u.set_password(pw)
                u.save()
            p, _ = Profile.objects.get_or_create(user=u)
            if not p.name:
                p.name = name
            p.bio = bio
            p.save()
            created.append(u)

        g, _ = ChatGroup.objects.get_or_create(name='friends_demo')
        for u in created:
            g.members.add(u)
        g.save()

        if len(created) >= 2:
            a = created[0]
            b = created[1]
            room = f'personal_{min(a.id,b.id)}_{max(a.id,b.id)}'
            Message.objects.create(sender=a, room_name=room, content='Hey there! This is a demo message from Alice.', timestamp=timezone.now())
            Message.objects.create(sender=b, room_name=room, content='Hi Alice — nice to meet you!', timestamp=timezone.now())

        Message.objects.create(sender=created[2], room_name=f'group_{g.id}', content='Welcome to the demo group!', timestamp=timezone.now())

        self.stdout.write(self.style.SUCCESS('Demo data created: users, group and messages.'))
