from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from .models import Room, Reservation
from .serializers import RoomSerializer, ReservationSerializer

# User management
@api_view(['POST'])
def create_user(request):
    data = request.data
    if User.objects.filter(username=data['username']).exists():
        return Response({'error': 'Username already exists'}, status=400)
    user = User.objects.create_user(data['username'], password=data['password'])
    return Response({'id': user.id})

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_user(request):
    user = request.user
    data = request.data
    user.username = data.get('username', user.username)
    user.set_password(data.get('password', user.password))
    user.save()
    return Response({'success': 'User updated'})

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_user(request):
    request.user.delete()
    return Response({'success': 'User deleted'})

# Room and reservation status
@api_view(['GET'])
def list_free_rooms(request):
    check_in = request.GET.get('check_in')
    if not check_in:
        return Response({'error': 'check_in parameter is required'}, status=400)
    rooms = Room.objects.exclude(reservation__check_in=check_in)
    serializer = RoomSerializer(rooms, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_all_rooms(request):
    check_in = request.GET.get('check_in')
    check_out = request.GET.get('check_out')
    if not check_in or not check_out:
        return Response({'error': 'check_in and check_out parameters are required'}, status=400)
    reservations = Reservation.objects.filter(check_in__lte=check_out, check_out__gte=check_in)
    rooms = Room.objects.all()
    data = []
    for room in rooms:
        reserved = False
        for reservation in reservations:
            if reservation.room == room:
                reserved = True
                break
        data.append({
            'room': room,
            'reserved': reserved,
            'reservations': ReservationSerializer(reservations.filter(room=room), many=True).data
        })
    return Response(data)

@api_view(['GET'])
def list_reservations(request):
    if request.user.is_authenticated:
        reservations = Reservation.objects.filter(user=request.user)
    else:
        reservations = Reservation.objects.none()
    serializer = ReservationSerializer(reservations, many=True)
    return Response(serializer.data)

# Reservation management
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_reservation(request):
    data = request.data
    try:
        room = Room.objects.get(id=data['room_id'])
    except Room.DoesNotExist:
        return Response({'error': 'Room not found'}, status=404)
    if room.reservation_set.filter(check_in=data['check_in']).exists():
        return Response({'error': 'Room already reserved for this day'}, status=400)
    reservation = Reservation.objects.create(user=request.user, room=room, check_in=data['check_in'], check_out=data['check_out'])
    serializer = ReservationSerializer(reservation)
    return Response(serializer.data)

api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def manage_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)
    if reservation.user != request.user:
        if not request.user.is_superuser:
            return Response({'error': 'You are not authorized to perform this action'}, status=403)

    if request.method == 'GET':
        serializer = ReservationSerializer(reservation)
        return Response(serializer.data)

    elif request.method == 'PUT':
        data = request.data
        try:
            room = Room.objects.get(id=data['room_id'])
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

# Room management
@api_view(['POST'])
@permission_classes([IsAdminUser])
def create_room(request):
    serializer = RoomSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)

@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def delete_room(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    room.delete()
    return Response({'success': 'Room deleted'})

@api_view(['PUT'])
@permission_classes([IsAdminUser])
def edit_room(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    serializer = RoomSerializer(room, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=400)

@api_view(['GET'])
def list_rooms(request):
    rooms = Room.objects.all()
    serializer = RoomSerializer(rooms, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_room(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    serializer = RoomSerializer(room)
    return Response(serializer.data)


# rewrite some views for readability and to avoid repetition