from django.urls import path
from .views import UserRegistrationView, UserLoginView, UserProfileView, UserChangePasswordView, \
    UserPasswordResetView, FinalPasswordResetView, UserLogoutView, OtpRefreshView, OtpSubmitView, ExtraDocDetailsView, \
    ExtraPatDetailsView,DocDetailsView

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name="register"),
    path('extra/doc/', ExtraDocDetailsView.as_view(), name="register"),
    path('extra/pat/', ExtraPatDetailsView.as_view(), name="register"),
    path('login/', UserLoginView.as_view(), name="login"),
    path('logout/', UserLogoutView.as_view(), name="logout"),
    path('otp/refresh/', OtpRefreshView.as_view(), name="logout"),
    path('otp/submit/', OtpSubmitView.as_view(), name="otpsubmit"),
    path('doc/details/', DocDetailsView.as_view(), name="docdetails"),
    path('profile/', UserProfileView.as_view(), name="profile"),
    path('changepass/', UserChangePasswordView.as_view(), name="changepass"),
    path('passreset/', UserPasswordResetView.as_view(), name="passreset"),
    path('finalpassreset/<uid>/<token>/', FinalPasswordResetView.as_view(), name="finalpassreset"),
]
