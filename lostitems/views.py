from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .forms import UserRegistrationForm, AuthenticationForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import LostItem, Message
from django.contrib.auth.models import User
import json

def index(request):
    return render(request, 'lostitems/landing.html')

def item_list(request):
    return render (request, 'lostitems/index.html')

@csrf_exempt
def create_item(request):
    if request.method == 'POST':
        try:
            title = request.POST.get('title')
            description = request.POST.get('description')
            location = request.POST.get('location')
            image = request.FILES.get('image')

            item = LostItem.objects.create(
                user=request.user,
                title=title,
                description=description,
                location=location,
                image=image
            )

            return JsonResponse({
                'status': 'success',
                'item': {
                    'id': item.id,
                    'title': item.title,
                    'description': item.description,
                    'location': item.location,
                    'date': item.date.isoformat(),
                    'image': item.image.url if item.image else None,
                }
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

def get_items(request):
    items = LostItem.objects.all().order_by('-created_at')
    items_data = [{
        'id': item.id,
        'title': item.title,
        'description': item.description,
        'location': item.location,
        'date': item.date.isoformat(),
        'image': item.image.url if item.image else None,
    } for item in items]
    return JsonResponse({'items': items_data})



def register_user(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('index')
    else:
        form = UserRegistrationForm()
    return render(request, 'lostitems/register.html', {'form': form})

def login_user(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                return redirect('index')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'lostitems/login.html', {'form': form})



@login_required
def logout_user(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect('index')



@login_required
@csrf_exempt
def create_message(request, item_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            item = get_object_or_404(LostItem, id=item_id)
            
            message = Message.objects.create(
                item=item,
                text=data['text'],
                sender=request.user, 
                receiver=item.user 
            )
            
            return JsonResponse({
                'status': 'success',
                'message': {
                    'id': message.id,
                    'text': message.text,
                    'sender': message.sender.username,
                    'timestamp': message.timestamp.isoformat()
                }
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)



@login_required
def get_messages(request, item_id):
    item = get_object_or_404(LostItem, id=item_id)
    
    if request.user != item.user and request.user not in item.messages.values_list('sender', flat=True):
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=403)
    
    messages = Message.objects.filter(item_id=item_id).order_by('timestamp')
    messages_data = [{
        'id': message.id,
        'text': message.text,
        'sender': message.sender.username,
        'is_current_user': message.sender == request.user,
        'timestamp': message.timestamp.isoformat()
    } for message in messages]
    
    return JsonResponse({
        'messages': messages_data,
        'item_owner': item.user.username
    })