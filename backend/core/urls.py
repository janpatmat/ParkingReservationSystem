from django.urls import path
from .views import AdminLoginView, ArchiveCreateView, CancelApprovedAndArchiveView, SimulatedTimeCheckView, CancelApprovedReservationView, ApprovedReservationsBySpotView, CancelReservationView, ApproveReservationView, ReserveUserListView, UserApprovedReservationView, UserReservationStatusView, ReserveCreateView, RegisterView, LoginView, AdminOnlyView, ParkingLocationCreateView, getLocation, getParkingSpot, ParkingSpotCreateView

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('login/', LoginView.as_view()),
    path('admin-only/', AdminOnlyView.as_view(), name='admin-only'),
    path('parking/create/', ParkingLocationCreateView.as_view()),
    path('parking/view/', getLocation.as_view()),
    path('parking/parkingspots/view/<int:location>/', getParkingSpot.as_view()),  # ← fixed
    path('parking/parkingspots/create/', ParkingSpotCreateView.as_view()),  # ← fixed
    path('reserve/create/', ReserveCreateView.as_view()),
    path('reserve/status/', UserReservationStatusView.as_view(), name='reservation-status'),
    path('reserve/users/<int:spot_id>/', ReserveUserListView.as_view()),
    path('reserve/cancel/<int:user_id>/', CancelReservationView.as_view()),
    path('reserve/approve/', ApproveReservationView.as_view()),
    path('approved-reservations/<int:spot_id>/', ApprovedReservationsBySpotView.as_view(), name='approved-reservations-by-spot'),
    path('approved-reservations/cancel/', CancelApprovedReservationView.as_view(), name='cancel-approved-reservation'),
    path('simulated-time/check/', SimulatedTimeCheckView.as_view(), name='simulated_time_check'),
    path('archive/', ArchiveCreateView.as_view(), name='archive-create'),
    path('approved/user/', UserApprovedReservationView.as_view(), name='user-approved-reservation'),
    path('approved/cancel/', CancelApprovedAndArchiveView.as_view(), name='cancel_approved_and_archive'),
    path('login/user/', LoginView.as_view(), name='user-login'),
    path('admin-login/', AdminLoginView.as_view(), name='admin-login'),
]
