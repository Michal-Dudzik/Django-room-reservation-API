from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import Room, Reservation
from .serializers import RoomSerializer, ReservationSerializer, UserSerializer
from datetime import date

@api_view(['GET', 'POST'])
def users(request):
    if request.method == 'GET':
        if not request.user.is_superuser:
            return Response({'error': 'You are not authorized to perform this action'}, status=403)
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        data = request.data
        if User.objects.filter(username=data['username']).exists():
            return Response({'error': 'Username already exists'}, status=400)
        user = User.objects.create_user(data['username'], password=data['password'])
        return Response({'id': user.id}, status=201)

@api_view(['GET','PUT', 'DELETE'])
def users_manage(request, user_id):
    user = get_object_or_404(User, id=user_id)  
    if request.method == 'GET':
        if not request.user.is_superuser and request.user != user:
            return Response({'error': 'You are not authorized to perform this action'}, status=403)
        serializer = UserSerializer(user)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        if not request.user.is_superuser and request.user != user:
            return Response({'error': 'You are not authorized to perform this action'}, status=403)
        data = request.data
        user.username = data.get('username', user.username)
        user.set_password(data.get('password', user.password))
        user.save()
        serializer = UserSerializer(user)
        return Response(serializer.data, status=200)
    
    elif request.method == 'DELETE':
        if not request.user.is_superuser and request.user != user:
            return Response({'error': 'You are not authorized to perform this action'}, status=403)
        user.delete()
        return Response({'success': 'User deleted'}, status=200)

@api_view(['GET', 'POST'])
def rooms(request):
    if request.method == 'GET':
        rooms = Room.objects.all()
        serializer = RoomSerializer(rooms, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        if not request.user.is_superuser:
            return Response({'error': 'You are not authorized to perform this action'}, status=403)
        serializer = RoomSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

@api_view(['GET', 'PUT', 'DELETE'])
def rooms_manage(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    if request.method == 'GET':
        serializer = RoomSerializer(room)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        if not request.user.is_superuser:
            return Response({'error': 'You are not authorized to perform this action'}, status=403)
        serializer = RoomSerializer(room, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
    
    elif request.method == 'DELETE':
        if not request.user.is_superuser:
            return Response({'error': 'You are not authorized to perform this action'}, status=403)
        room.delete()
        return Response({'success': 'Room deleted'}, status=200)
    
@api_view(['GET'])
def free_rooms(request):
    check_in = request.GET.get('check_in')
    if not check_in:
        return Response({'error': 'Missing check-in date'}, status=400)
    try:
        check_in = date.fromisoformat(check_in)
    except ValueError:
        return Response({'error': 'Invalid date format (YYYY-MM-DD)'}, status=400)
    
    reservations = Reservation.objects.filter(
        Q(check_in__lte=check_in) & Q(check_out__gte=check_in)
        | Q(check_in__gte=check_in) & Q(check_in__lte=check_in)
    )
    reserved_room_ids = reservations.values_list('room__id', flat=True)
    free_rooms = Room.objects.exclude(id__in=reserved_room_ids)
    serializer = RoomSerializer(free_rooms, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def rooms_status(request):
    if 'check_in' not in request.GET or 'check_out' not in request.GET:
        return Response({'error': 'Missing check_in or check_out parameter'}, status=400)
    
    check_in = request.GET['check_in']
    check_out = request.GET['check_out']
    
    rooms = Room.objects.all()
    data = []
    for room in rooms:
        reserved_dates = Reservation.objects.filter(room=room).filter(
            Q(check_in__gte=check_in, check_in__lt=check_out) |
            Q(check_out__gt=check_in, check_out__lte=check_out) |
            Q(check_in__lte=check_in, check_out__gte=check_out)
        ).values_list('check_in', 'check_out')
        
        room_data = {
            'number': room.number,
            'floor': room.floor,
            'description': room.description,
            'status': 'free' if not reserved_dates else 'reserved',
            'reserved_dates': reserved_dates
        }
        data.append(room_data)
    
    return Response(data)

@api_view(['GET', 'POST'])
def reservations(request):
    if request.method == 'GET':
        reservations = Reservation.objects.all()
        serializer = ReservationSerializer(reservations, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        if not request.user.is_authenticated:
            return Response({'error': 'You are not authorized to perform this action'}, status=403)
        data = request.data
        try:
            room_id = int(data.get('room'))
        except (ValueError, TypeError):
            return Response({'error': 'Invalid room ID'}, status=400)
        try:
            room = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            return Response({'error': 'Room not found'}, status=404)
        if room.reservation_set.filter(check_in=data['check_in']).exists():
            return Response({'error': 'Room already reserved for this day'}, status=400)
        serializer = ReservationSerializer(data=data)
        if serializer.is_valid():
            serializer.save(user=request.user, room=room)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    
@api_view(['GET', 'PUT', 'DELETE'])
def reservations_manage(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)
    if request.method == 'GET':
        serializer = ReservationSerializer(reservation)
        return Response(serializer.data)

    elif request.method == 'PUT':
        data = request.data
        try:
            room = Room.objects.get(id=data['room'])
        except Room.DoesNotExist:
            return Response({'error': 'Room not found'}, status=404)
        if room.reservation_set.filter(check_in=data['check_in']).exclude(id=reservation.id).exists():
            return Response({'error': 'Room already reserved for this day'}, status=400)
        reservation.room = room
        reservation.check_in = data['check_in']
        reservation.check_out = data['check_out']
        reservation.save()
        serializer = ReservationSerializer(reservation)
        return Response(serializer.data)

    elif request.method == 'DELETE':
        reservation.delete()
        return Response({'success': 'Reservation deleted'})