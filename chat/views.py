from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from .forms import RegisterForm, ProfileForm
from django.contrib.auth.models import User
from .models import Profile, Message, ChatGroup
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET, require_POST
from django.db.models import Q
from django.utils import timezone
import json


def welcome_view(request):
    return render(request, 'chat/welcome.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        pw = request.POST.get('password')
        user = authenticate(request, username=username, password=pw)
        if user:
            login(request, user)
            return redirect('chat:home')
        else:
            return render(request, 'chat/login.html', {'error': 'Invalid credentials'})
    return render(request, 'chat/login.html')


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
            )
            Profile.objects.create(user=user)
            login(request, user)
            return redirect('chat:home')
    else:
        form = RegisterForm()
    return render(request, 'chat/register.html', {'form': form})


@login_required
def home(request):
    """
    Renders the main chat UI. If you pass ?demo=1 it will include some fake
    groups/users/messages in the template context for preview/demo purposes
    (no DB writes).
    """
    profile = Profile.objects.get(user=request.user)
    groups = request.user.chat_groups.all()
    messages = Message.objects.filter(room_name__icontains=f'{request.user.id}').order_by('-timestamp')[:20]

    demo = request.GET.get('demo') == '1'
    demo_users = []
    demo_groups = []
    demo_messages = []
    if demo:
        demo_users = [
            {'username': 'alice', 'display_name': 'Alice A', 'bio': 'Loves photography'},
            {'username': 'bob', 'display_name': 'Bob B', 'bio': 'Coffee fan'},
            {'username': 'carol', 'display_name': 'Carol C', 'bio': 'Traveler'},
        ]
        demo_groups = [
            {'id': 1, 'name': 'Best Friends', 'members': ['alice','bob','asish']},
            {'id': 2, 'name': 'Project Team', 'members': ['asish','carol']},
        ]
        demo_messages = [
            {'sender': 'alice', 'content': 'Hey — demo message', 'timestamp': timezone.now().isoformat()},
            {'sender': request.user.username, 'content': 'Nice demo!', 'timestamp': timezone.now().isoformat()},
        ]

    return render(request, 'chat/home.html', {
        'profile': profile,
        'messages': messages,
        'groups': groups,
        'demo': demo,
        'demo_users': demo_users,
        'demo_groups': demo_groups,
        'demo_messages': demo_messages,
    })


@login_required
def logout_view(request):
    logout(request)
    return redirect('chat:login')


@login_required
def edit_profile(request):
    profile = Profile.objects.get(user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            p = form.save(commit=False)
            if not p.name:
                p.name = ''
            p.save()
            return redirect('chat:view_profile', username=request.user.username)
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'chat/profile.html', {'form': form, 'profile': profile})


def view_profile(request, username):
    user = get_object_or_404(User, username=username)
    profile = Profile.objects.get(user=user)

    is_own = request.user.is_authenticated and request.user.username == username

    return render(request, 'chat/view_profile.html', {'profile': profile, 'is_own': is_own})


@require_GET
def username_check(request):
    q = request.GET.get('q', '').strip()
    exists = False
    if q:
        exists = User.objects.filter(username=q).exists()
    return JsonResponse({'exists': exists})


def ws_test(request):
    return HttpResponse("ws-test OK")


@require_GET
def search_users(request):
    """
    Returns JSON list of users matching the query 'q'.
    Each item: { id, username, display_name, bio }
    Excludes inactive users.
    """
    q = request.GET.get('q', '').strip()
    results = []
    if q:
        qs = User.objects.filter(
            Q(username__icontains=q) | Q(profile__name__icontains=q)
        ).select_related('profile')[:30]
    else:
        qs = User.objects.all().select_related('profile')[:30]

    for u in qs:
        if not u.is_active:
            continue
        p = None
        try:
            p = u.profile
        except Profile.DoesNotExist:
            p = None
        results.append({
            'id': u.id,
            'username': u.username,
            'display_name': p.display_name() if p else u.username,
            'bio': p.bio if p else '',
        })
    return JsonResponse({'results': results})


@login_required
@require_GET
def get_personal_room(request):
    """
    Given ?username=other, returns canonical personal room name for current user + other.
    Room uses sorted user ids: personal_<minid>_<maxid>
    """
    other = request.GET.get('username', '').strip()
    if not other:
        return JsonResponse({'error': 'missing username'}, status=400)
    try:
        other_user = User.objects.get(username=other)
    except User.DoesNotExist:
        return JsonResponse({'error': 'user not found'}, status=404)
    a = request.user.id
    b = other_user.id
    lo, hi = (a, b) if a < b else (b, a)
    room = f'personal_{lo}_{hi}'
    return JsonResponse({'room': room, 'other': other_user.username})


@login_required
@require_POST
def send_message(request):
    """
    Fallback POST endpoint for saving messages. This will be used by the frontend
    if WebSocket isn't connected. Request must be JSON: { room: "...", message: "..." }.
    Returns saved message JSON.
    """
    try:
        payload = json.loads(request.body.decode('utf-8'))
    except Exception:
        return HttpResponseBadRequest("Invalid JSON")

    room = payload.get('room', '').strip()
    text = payload.get('message', '').strip()
    if not room or not text:
        return JsonResponse({'error': 'missing room or message'}, status=400)

    msg = Message.objects.create(room_name=room, sender=request.user, content=text, timestamp=timezone.now())
    return JsonResponse({
        'ok': True,
        'message': {
            'id': msg.id,
            'sender': msg.sender.username,
            'content': msg.content,
            'timestamp': msg.timestamp.isoformat(),
        }
    })
