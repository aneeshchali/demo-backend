from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView,ListAPIView
from rest_framework.views import status
from rest_framework.views import APIView
from .serializers import UserRegistrationSerializer, UserLoginSerializer, UserProfileSerializer, \
    UserChangePasswordSerializer, UserPasswordResetSerializer, FinalPasswordResetSerializer, LogoutTokenSerializer, \
    SubmitOtpSerializer, ExtraDocDetailsSerializer,ExtraPatDetailsSerializer,DocSettingDetailsSerializers,PatSettingsDetailsSerializer
from django.contrib.auth import authenticate, logout
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, AllowAny
from .helpers import OtpGenerator
# import datetime
from .models import Doctor,Patient

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class UserRegistrationView(APIView):
    def post(self, request, format=None):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            token = get_tokens_for_user(user)
            return Response({'token': token, 'message': 'Successfull'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ExtraDocDetailsView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, format=None):
        print(request.data)
        serializer = ExtraDocDetailsSerializer(data=request.data, context={'user': request.user})
        if serializer.is_valid(raise_exception=True):
            return Response({'message': 'Successfull Update!'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, format=None):
        doctor = Doctor.objects.get(user=request.user)
        serializer = DocSettingDetailsSerializers(doctor)
        print(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ExtraPatDetailsView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, format=None):
        serializer = ExtraPatDetailsSerializer(data=request.data, context={'user': request.user})
        if serializer.is_valid(raise_exception=True):
            return Response({'message': 'Successfull Update!'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, format=None):
        patient = Patient.objects.get(user=request.user)
        serializer = PatSettingsDetailsSerializer(patient)
        print(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)
    # def get(self,request,format=None):
    #     serializer = docSettingsListSerializer(request.user)
    #     return Response(serializer.data, status=status.HTTP_200_OK)

class ImgUploadView(APIView):
    permission_classes = [IsAuthenticated]
    def put(self,request):
        user = request.user
        if user.is_staff:
            doctor = Doctor.objects.get(user=request.user)
            doctor.img = request.data["data"]
            doctor.save()
        else:
            patient = Patient.objects.get(user=request.user)
            patient.img = request.data["data"]
            patient.save()
        return Response({'message': 'Successfull Update!'}, status=status.HTTP_201_CREATED)




class UserLoginView(APIView):
    def post(self, request, format=None):
        print(request.data)
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            email = serializer.data.get('email')
            password = serializer.data.get('password')
            user = authenticate(email=email, password=password)
            if user is not None:
                token = get_tokens_for_user(user)
                return Response({"token": token, "type": user.is_staff, "verified": user.is_verified,
                                 "details": user.details_status,"username":user.name}, status=status.HTTP_200_OK)
            else:
                return Response({'errors': 'Email or Password is not Valid'},
                                status=status.HTTP_400_BAD_REQUEST)


# class UserLogoutView(APIView):
#
#     def post(self, request, format=None):
#         request.user.auth_token.delete()
#         data = {'success': 'Sucessfully logged out'}
#         return Response(data=data, status=status.HTTP_200_OK)

class UserLogoutView(GenericAPIView):
    serializer_class = LogoutTokenSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args):
        sz = self.get_serializer(data=request.data)
        sz.is_valid(raise_exception=True)
        sz.save()
        return Response(status=status.HTTP_204_NO_CONTENT)




class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


# class StandardResultsSetPagination(PageNumberPagination):
#     page_size = 5
#     page_size_query_param = 'page_size'
#     max_page_size = 10
#
# class DocDetailsView(ListAPIView):
#     pagination_class = StandardResultsSetPagination
#     queryset = Doctor.objects.filter(details_status=True).all()
#     serializer_class = DocSettingDetailsSerializers


class OtpRefreshView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        user = request.user
        user.otp = OtpGenerator.generateOTP()
        user.save()
        return Response({'message': "New Otp Sent."}, status=status.HTTP_200_OK)


class OtpSubmitView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        serializer = SubmitOtpSerializer(data=request.data, context={'user': request.user})
        if serializer.is_valid(raise_exception=True):

            return Response({'message': "Success!"}, status=status.HTTP_200_OK)


class UserChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        serializer = UserChangePasswordSerializer(data=request.data, context={'user': request.user})
        if serializer.is_valid(raise_exception=True):
            return Response({'message': "password Changed!"}, status=status.HTTP_200_OK)


class UserPasswordResetView(APIView):
    permission_classes = []

    def post(self, request, format=None):
        serializer = UserPasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({"message": "Passsword Reset Link Sent to your Registered Email"}, status=status.HTTP_200_OK)


class FinalPasswordResetView(APIView):
    def post(self, request, uid, token, format=None):
        serializer = FinalPasswordResetSerializer(data=request.data, context={'uid': uid, 'token': token})
        serializer.is_valid(raise_exception=True)
        return Response({"message": "Password Reset Successfully"}, status=status.HTTP_200_OK)
