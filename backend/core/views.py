from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from django.contrib.auth.models import User
from rest_framework.decorators import api_view
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework import status
from .serializers import ArchiveSerializer, ParkingLocationSerializer, parkingSpotSerializer
from .models import parkingLocation, parkingSpot, reserveTable, approvedreserveTable, Archive
from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_datetime
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response({"error": "Username and password are required."}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({"error": "Username already exists."}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=username, password=password)
        user.is_staff = False  # explicitly ensure it's not admin
        user.save()

        return Response({
            "message": "User registered successfully.",
            "username": user.username,
            "is_staff": user.is_staff
        }, status=status.HTTP_201_CREATED)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)
        
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'username': user.username,
                'is_staff': user.is_staff,  # admin = True
                
            })

        return Response({"error": "Invalid credentials"}, status=401)
    
class AdminOnlyView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_staff:
            return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
        return Response({"message": "Welcome, Admin!"})


class ParkingLocationCreateView(APIView):
    def post(self, request):
        serializer = ParkingLocationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class getLocation(APIView):
    permission_classes = [IsAuthenticated]
    # permission_classes = [AllowAny]

    def get(self , request):
        # if not request.user.is_staff:
        #      return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
        
        locations = parkingLocation.objects.all()

        serializer = ParkingLocationSerializer(locations, many=True)

        return Response(serializer.data)
    

class getParkingSpot(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, location):

        
        parkingspots = parkingSpot.objects.filter(location=location)

        serializer = parkingSpotSerializer(parkingspots, many=True)
        return Response(serializer.data)
    
class ParkingSpotCreateView(APIView):
    def post(self, request):
        serializer = parkingSpotSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReserveCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            customer = request.user
            spot_id = request.data.get('spotID')
            date_in = request.data.get('date_in')
            date_out = request.data.get('date_out')

            if not all([spot_id, date_in, date_out]):
                return Response({'error': 'spotID, date_in, and date_out are required.'},
                                status=status.HTTP_400_BAD_REQUEST)

            # Get the parking spot
            spot = get_object_or_404(parkingSpot, pk=spot_id)

            # Create reservation
            reservation = reserveTable.objects.create(
                spotID=spot,
                customerID=customer,
                date_in=date_in,
                date_out=date_out
            )

            return Response({
                'reserveID': reservation.reserveID,
                'spotID': reservation.spotID.spotID,
                'customerID': reservation.customerID.id,
                'date_in': reservation.date_in,
                'date_out': reservation.date_out,
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class UserReservationStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        has_reservation = reserveTable.objects.filter(customerID=user).exists()
        return Response({"has_reservation": has_reservation})  
    

class ReserveUserListView(APIView):
    permission_classes = [IsAdminUser]  # Optional: restrict to admins

    def get(self, request, spot_id):
        reservations = reserveTable.objects.filter(spotID__spotID=spot_id).select_related('customerID')

        data = []
        for res in reservations:
            user = res.customerID
            data.append({
                'reservation_id': res.reserveID,
                'spot_id': res.spotID.spotID,
                'user_id': user.id,
                'username': user.username,
                'is_staff': user.is_staff,
                'date_in': res.date_in.isoformat() if res.date_in else None,
                'date_out': res.date_out.isoformat() if res.date_out else None,
            })

        return Response(data, status=status.HTTP_200_OK)

class ApproveReservationView(APIView):
    def post(self, request):
        spot_id = request.data.get('spot_id')
        user_id = request.data.get('user_id')
        approved_reserve_id = request.data.get('approved_reserve_id')  # this is the reserveTable ID to delete
        date_in = request.data.get('date_in')
        date_out = request.data.get('date_out')

        try:
            # Validate inputs
            if not all([spot_id, user_id, approved_reserve_id, date_in, date_out]):
                return Response({'error': 'All fields are required.'}, status=status.HTTP_400_BAD_REQUEST)

            # Get parking spot and user
            spot = get_object_or_404(parkingSpot, pk=spot_id)
            user = get_object_or_404(User, pk=user_id)

            # Create approved reservation
            approved = approvedreserveTable.objects.create(
                spotID=spot,
                customerID=user,
                date_in=date_in,
                date_out=date_out
            )

            # Assign to spot
            
            spot.save()

            # Delete from reserveTable
            reserveTable.objects.filter(pk=approved_reserve_id).delete()

            return Response({
                'message': 'Reservation approved, approved record saved, and pending reservation deleted.',
                'approved_id': approved.approvedreserveID
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class CancelReservationView(APIView):
    def delete(self, request, user_id):
        try:
            reservations = reserveTable.objects.filter(customerID=user_id)
            archived_count = 0

            for res in reservations:
                Archive.objects.create(
                    customer_name=res.customerID.username,
                    spotID=res.spotID,
                    date_in=res.date_in,
                    date_out=res.date_out,
                    status="canceled"
                )
                archived_count += 1

            deleted_count, _ = reservations.delete()

            return Response({'message': f'{archived_count} reservation(s) archived and {deleted_count} deleted.'},
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        

class ApprovedReservationsBySpotView(APIView):
    def get(self, request, spot_id):
        reservations = approvedreserveTable.objects.filter(spotID__spotID=spot_id).select_related('customerID')
        
        data = []
        for r in reservations:
            data.append({
                'approvedreserveID': r.approvedreserveID,
                'spotID': r.spotID.spotID if r.spotID else None,
                'customerID': r.customerID.id if r.customerID else None,
                'customerUsername': r.customerID.username if r.customerID else None,
                'date_in': r.date_in,
                'date_out': r.date_out,
            })

        return Response(data, status=status.HTTP_200_OK)

class CancelApprovedReservationView(APIView):
    def post(self, request):
        approved_id = request.data.get('approvedreserveID')

        if not approved_id:
            return Response({'error': 'approvedreserveID is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            reservation = approvedreserveTable.objects.get(pk=approved_id)

            # Archive before deletion
            Archive.objects.create(
                customer_name=reservation.customerID.username,
                spotID=reservation.spotID,
                date_in=reservation.date_in,
                date_out=reservation.date_out,
                status="canceled"
            )

            reservation.delete()

            return Response({'message': 'Reservation cancelled and archived'}, status=status.HTTP_200_OK)

        except approvedreserveTable.DoesNotExist:
            return Response({'error': 'Reservation not found'}, status=status.HTTP_404_NOT_FOUND)


class ArchiveCreateView(APIView):
    def post(self, request):
        serializer = ArchiveSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Reservation archived successfully.'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class CancelApprovedAndArchiveView(APIView):
    def post(self, request):
        approved_id = request.data.get('approvedreserveID')

        if not approved_id:
            return Response({'error': 'approvedreserveID is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            reservation = approvedreserveTable.objects.get(pk=approved_id)

            # Archive the canceled reservation
            # Archive.objects.create(
            #     customer_name=reservation.customerID.username if reservation.customerID else "Unknown",
            #     spotID=reservation.spotID,
            #     date_in=reservation.date_in,
            #     date_out=reservation.date_out,
            #     status='canceled'
            # )

            reservation.delete()

            return Response({'message': 'Reservation canceled and archived.'}, status=status.HTTP_200_OK)

        except approvedreserveTable.DoesNotExist:
            return Response({'error': 'Reservation not found'}, status=status.HTTP_404_NOT_FOUND)
            
class SimulatedTimeCheckView(APIView):
    def post(self, request):
        current_time = request.data.get('current_time')
        if not current_time:
            return Response({'error': 'current_time is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            now = parse_datetime(current_time)

            # === Handle expired pending reservations ===
            expired_reserves = reserveTable.objects.filter(date_out__lt=now)
            for res in expired_reserves:
                Archive.objects.create(
                    customer_name=res.customerID.username,
                    spotID=res.spotID,
                    date_in=res.date_in,
                    date_out=res.date_out,
                    status="canceled"
                )
            expired_reserves.delete()

            # === Handle expired approved reservations ===
            expired_approved = approvedreserveTable.objects.filter(date_out__lt=now)
            for entry in expired_approved:
                Archive.objects.create(
                    customer_name=entry.customerID.username,
                    spotID=entry.spotID,
                    date_in=entry.date_in,
                    date_out=entry.date_out,
                    status="finished"
                )
                entry.spotID.save()
                entry.delete()

            return Response({'message': 'Expired reservations cleaned and archived.'}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class UserApprovedReservationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user  # Automatically resolved from JWT
        try:
            reservation = approvedreserveTable.objects.filter(customerID=user).first()

            if not reservation:
                return Response({"message": "No approved reservation found."}, status=status.HTTP_404_NOT_FOUND)

            data = {
                "approvedreserveID": reservation.approvedreserveID,
                "spotID": reservation.spotID.spotID if reservation.spotID else None,
                "date_in": reservation.date_in,
                "date_out": reservation.date_out,
                "customerID": user.id,
                "customerUsername": user.username
            }

            return Response(data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
