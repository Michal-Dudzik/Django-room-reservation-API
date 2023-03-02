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
    path('', views.rooms, name='rooms'),
    path('admin/', admin.site.urls),
    path('users/', views.users, name='users'),
    path('users/manage/<int:user_id>/', views.users_manage, name='users-manage'),
    path('rooms/', views.rooms, name='rooms'),
    path('rooms/manage/<int:room_id>/', views.rooms_manage, name='rooms-manage'),
    path('reservations/', views.reservations, name='reservations'),
    path('reservations/manage/<int:reservation_id>/', views.reservations_manage, name='reservations-manage'),
    path('rooms/free/', views.free_rooms, name='free-rooms'),
    path('rooms/status/', views.rooms_status, name='rooms-status'),
]

urlpatterns = format_suffix_patterns(urlpatterns)