"""hotel URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from . import views


# from hotel.views import RoomList, RoomDetails

urlpatterns = [
    path('admin/', admin.site.urls),
    path('rooms/', views.list_rooms, name='room-list'),
    path('rooms/<int:room_id>/', views.edit_room, name='room-detail'),
    path('rooms/free/', views.list_free_rooms, name='free-room-list'),
    path('rooms/all/', views.list_all_rooms, name='all-room-list'),
    path('users/create/', views.create_user, name='user-create'),
    path('users/edit/', views.update_user, name='user-edit'),
    path('users/delete/', views.delete_user, name='user-delete'),
    path('reservations/', views.list_reservations, name='reservation-list'),
    path('reservations/create/', views.create_reservation, name='reservation-create'),
    path('reservations/<int:reservation_id>/edit/', views.manage_reservation, name='reservation-edit'),
    path('reservations/<int:reservation_id>/delete/', views.manage_reservation, name='reservation-delete'),
    path('rooms/create/', views.create_room, name='room-create'),
    path('rooms/<int:room_id>/edit/', views.edit_room, name='room-edit'),
]

urlpatterns = format_suffix_patterns(urlpatterns)