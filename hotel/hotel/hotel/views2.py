# from django.contrib.auth.models import User
from .models import Room, Reservation
from .serializers import RoomSerializer, ReservationSerializer, UserSerializer
from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser

import datetime
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.db.models import Q 
from rest_framework.authentication import TokenAuthentication

# //////////Room management//////////
# Show all rooms and add a new one
@api_view(['GET', 'POST'])
def room_list(request, format = None):
    if request.method == 'GET':
        rooms = Room.objects.all()
        serializer = RoomSerializer(rooms, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = RoomSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

# get details of a specific room, update it or delete it
@api_view(['GET', 'PUT', 'DELETE'])
def room_detail(request, pk, format = None):
    try:
        Room.objects.get(pk=pk)
    except Room.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        room = Room.objects.get(pk=pk)
        serializer = RoomSerializer(room)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        room = Room.objects.get(pk=pk)
        serializer = RoomSerializer(room, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        room = Room.objects.get(pk=pk)
        room.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
  
# ///////////////Jeszcze nie przetestowane mogą się sypać !!!!/////////////////////

# get rooms and their status for a certain period
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def room_status(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    daterange = lambda start_date, end_date: (start_date + datetime.timedelta(n) for n in range(int((end_date - start_date).days) + 1))

    if not start_date or not end_date:
        return Response({'error': 'Please provide both start_date and end_date parameters.'},
                        status=status.HTTP_400_BAD_REQUEST)

    try:
        start_date_obj = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date_obj = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
    except ValueError:
        return Response({'error': 'Invalid date format. Expected format: YYYY-MM-DD.'},
                        status=status.HTTP_400_BAD_REQUEST)

    rooms = Room.objects.all()
    data = []

    for room in rooms:
        room_data = {'room_number': room.number, 'room_floor': room.floor, 'room_description': room.description}
        availability = []

        for single_date in daterange(start_date_obj, end_date_obj):
            reservation = Reservation.objects.filter(room=room, date=single_date).first()

            if reservation:
                availability.append({'date': single_date, 'available': False, 'user': reservation.user.username})
            else:
                availability.append({'date': single_date, 'available': True, 'user': ''})

        room_data['availability'] = availability
        data.append(room_data)

    return Response(data)

# get a list of free rooms on a given date
@api_view(['GET'])
def free_rooms(request, date):
    try:
        date_obj = datetime.datetime.strptime(date, '%Y-%m-%d').date()
    except ValueError:
        return Response({'error': 'Invalid date format. Expected format: YYYY-MM-DD.'},
                        status=status.HTTP_400_BAD_REQUEST)

    free_rooms = Room.objects.filter(~Q(reservations__date=date_obj)).distinct()
    serializer = RoomSerializer(free_rooms, many=True)
    return Response(serializer.data)

# //////////User management//////////
# # create new user account
# @api_view(['POST'])
# def create_account(request):
#     serializer = UserSerializer(data=request.data)
#     if serializer.is_valid():
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# # Login user and return authentication token
# @api_view(['POST'])
# def login_user(request):
#     username = request.data.get('username')
#     password = request.data.get('password')
#     user = authenticate(username=username, password=password)
#     if user is not None:
#         login(request, user)
#         return JsonResponse({'token': user.auth_token.key})
#     else:
#         return JsonResponse({'error': 'Invalid Credentials'}, status=status.HTTP_400_BAD_REQUEST)

# # edit or delete user account
# @api_view(['GET', 'PUT', 'DELETE'])
# @permission_classes([IsAuthenticated])
# def manage_account(request, pk, format = None):

@api_view(['POST'])
def create_user(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = User.objects.create_user(
            username=serializer.validated_data['username'],
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password']
        )
        token = TokenAuthentication.objects.create(user=user)
        return Response({'token': token.key}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def user_detail(request):
    user = request.user
    if request.method == 'GET':
        serializer = UserSerializer(user)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)
    if user is not None:
        token, _ = TokenAuthentication.objects.get_or_create(user=user)
        return Response({'token': token.key}, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    request.user.auth_token.delete()
    return Response(status=status.HTTP_200_OK)

# //////////Reservation management//////////
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_reservation(request):
    serializer = ReservationSerializer(data=request.data)
    if serializer.is_valid():
        # check if room is available on the requested date
        room = serializer.validated_data['room']
        date = serializer.validated_data['date']
        existing_reservation = Reservation.objects.filter(room=room, date=date).first()
        if existing_reservation is not None:
            return Response({'error': 'Room is already reserved on the requested date.'}, status=status.HTTP_400_BAD_REQUEST)
        # create reservation
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def manage_reservation(request, pk):
    try:
        reservation = Reservation.objects.get(pk=pk)
    except Reservation.DoesNotExist:
        return Response({'error': 'Reservation not found.'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ReservationSerializer(reservation)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = ReservationSerializer(reservation, data=request.data)
        if serializer.is_valid():
            # check if room is available on the requested date
            room = serializer.validated_data['room']
            date = serializer.validated_data['date']
            existing_reservation = Reservation.objects.filter(room=room, date=date).exclude(pk=pk).first()
            if existing_reservation is not None:
                return Response({'error': 'Room is already reserved on the requested date.'}, status=status.HTTP_400_BAD_REQUEST)
            # update reservation
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        reservation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)