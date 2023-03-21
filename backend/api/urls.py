from django.urls import path
from .views import DocDetailsView

urlpatterns = [
    path('list/', DocDetailsView.as_view(), name="register"),
]
