from django.urls import path
from .views import DocDetailsView,DocSpecialityView

urlpatterns = [
    path('list/', DocDetailsView.as_view(), name="register"),
    path('specialist/', DocSpecialityView.as_view(), name="register"),
]
