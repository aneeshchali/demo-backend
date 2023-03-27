from django.urls import path
from .views import DocDetailsView,DocSpecialityView,SlotBookingView

urlpatterns = [
    path('list/', DocDetailsView.as_view(), name="register"),
    path('specialist/', DocSpecialityView.as_view(), name="register2"),
    path('bookslot/', SlotBookingView.as_view(), name="bookslot"),
]
