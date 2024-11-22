from django.db import models
from django.utils import timezone

class LostItem(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=200)
    date = models.DateField(default=timezone.now)
    image = models.ImageField(upload_to='lost_items/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Message(models.Model):
    item = models.ForeignKey(LostItem, related_name='messages', on_delete=models.CASCADE)
    text = models.TextField()
    sender = models.CharField(max_length=50)  # 'user' or 'other'
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message for {self.item.title} at {self.timestamp}"
