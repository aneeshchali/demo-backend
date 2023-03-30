from django.urls import path
from .views import DocDetailsView,DocSpecialityView,SlotBookingView,DashboardTableView,ConnectCallView

urlpatterns = [
    path('list/', DocDetailsView.as_view(), name="register"),
    path('specialist/', DocSpecialityView.as_view(), name="register2"),
    path('bookslot/', SlotBookingView.as_view(), name="bookslot"),
    path('dashtable/', DashboardTableView.as_view(), name="dashtable"),
    path('call/connect/', ConnectCallView.as_view(), name="callConnect"),
]
