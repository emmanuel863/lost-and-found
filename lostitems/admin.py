from django.contrib import admin
from .models import LostItem, Message

# Register LostItem model
@admin.register(LostItem)
class LostItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'location', 'date', 'created_at')
    search_fields = ('title', 'description', 'location')
    list_filter = ('date', 'created_at')

# Register Message model
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('item', 'sender', 'timestamp')
    list_filter = ('sender', 'timestamp')
    search_fields = ('text', 'sender')
