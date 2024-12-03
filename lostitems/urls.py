from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path('items/', views.item_list, name='item_list'),
    path('api/items/', views.get_items, name='get_items'),
    path('api/items/create/', views.create_item, name='create_item'),
    path('api/items/<int:item_id>/messages/', views.get_messages, name='get_messages'),
    path('api/items/<int:item_id>/messages/create/', views.create_message, name='create_message'),
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 