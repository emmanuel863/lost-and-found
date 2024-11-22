from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import LostItem, Message
import json

def index(request):
    return render(request, 'lostitems/index.html')

@csrf_exempt
def create_item(request):
    if request.method == 'POST':
        try:
            title = request.POST.get('title')
            description = request.POST.get('description')
            location = request.POST.get('location')
            image = request.FILES.get('image')

            item = LostItem.objects.create(
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

@csrf_exempt
def create_message(request, item_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            item = LostItem.objects.get(id=item_id)
            message = Message.objects.create(
                item=item,
                text=data['text'],
                sender=data['sender']
            )
            return JsonResponse({
                'status': 'success',
                'message': {
                    'id': message.id,
                    'text': message.text,
                    'sender': message.sender,
                    'timestamp': message.timestamp.isoformat()
                }
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

def get_messages(request, item_id):
    messages = Message.objects.filter(item_id=item_id).order_by('timestamp')
    messages_data = [{
        'id': message.id,
        'text': message.text,
        'sender': message.sender,
        'timestamp': message.timestamp.isoformat()
    } for message in messages]
    return JsonResponse({'messages': messages_data})
