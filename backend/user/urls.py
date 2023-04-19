from django.urls import path
from .views import UserRegistrationView, UserLoginView, UserProfileView, UserChangePasswordView, \
    UserPasswordResetView, FinalPasswordResetView, UserLogoutView, OtpRefreshView, OtpSubmitView, ExtraDocDetailsView, \
    ExtraPatDetailsView,ImgUploadView,UserGRegistrationView,GUserLoginView #DocDetailsView,

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name="register"),
    path('gregister/', UserGRegistrationView.as_view(), name="gregister"),
    path('extra/doc/', ExtraDocDetailsView.as_view(), name="extradoc"),
    path('extra/pat/', ExtraPatDetailsView.as_view(), name="extrapat"),
    path('img/upload/', ImgUploadView.as_view(), name="imgupload"),
    path('login/', UserLoginView.as_view(), name="login"),
    path('glogin/', GUserLoginView.as_view(), name="glogin"),
    path('logout/', UserLogoutView.as_view(), name="logout"),
    path('otp/refresh/', OtpRefreshView.as_view(), name="otprefresh"),
    path('otp/submit/', OtpSubmitView.as_view(), name="otpsubmit"),
    # path('doc/details/', DocDetailsView.as_view(), name="docdetails"),
    path('profile/', UserProfileView.as_view(), name="profile"),
    path('changepass/', UserChangePasswordView.as_view(), name="changepass"),
    path('passreset/', UserPasswordResetView.as_view(), name="passreset"),
    path('finalpassreset/<uid>/<token>/', FinalPasswordResetView.as_view(), name="finalpassreset"),
]
