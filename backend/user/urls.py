from django.urls import path
from .views import UserRegistrationView, UserLoginView, UserProfileView, UserChangePasswordView, \
    UserPasswordResetView, FinalPasswordResetView

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name="register"),
    path('login/', UserLoginView.as_view(), name="login"),
    path('profile/', UserProfileView.as_view(), name="profile"),
    path('changepass/', UserChangePasswordView.as_view(), name="changepass"),
    path('passreset/', UserPasswordResetView.as_view(), name="passreset"),
    path('finalpassreset/<uid>/<token>/', FinalPasswordResetView.as_view(), name="finalpassreset"),
]
