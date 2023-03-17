from xml.dom import ValidationErr
from rest_framework import serializers
from .models import User, Doctor

# below import for Password reset email and encode and decode:
from django.utils.encoding import smart_str, force_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import PasswordResetTokenGenerator

from django.utils.text import gettext_lazy as _
from rest_framework_simplejwt.tokens import RefreshToken, TokenError


class UserRegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = ['email', 'name', 'is_staff', 'password', 'password2']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')
        if password != password2:
            raise serializers.ValidationError("password does't match")
        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class ExtraDocDetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Doctor
        fields = ['phone', 'qualification', 'speciality', 'hosp_name', 'experience', 'fees', 'slot_start', 'slot_end',
                  'age', 'gender']
    #
    # def update(self, instance, validated_data):
    #     return Doctor.objects.fil


class UserLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255)

    class Meta:
        model = User
        fields = ['email', 'password']


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'name']


class SubmitOtpSerializer(serializers.Serializer):
    otp = serializers.CharField(max_length=6, write_only=True)

    class Meta:
        fields = ['otp']

    def validate(self, attrs):
        otp = attrs.get('otp')
        print(otp)
        user = self.context.get('user')
        userOTP = user.otp
        if int(userOTP) == int(otp):
            user.is_verified = True
            user.save()
        else:
            raise serializers.ValidationError("Otp is Invalid")
        return attrs


class UserChangePasswordSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=255, style={"input_type": "password"}, write_only=True)
    password2 = serializers.CharField(max_length=255, style={"input_type": "password"}, write_only=True)

    class Meta:
        fields = ['password', 'password2']

    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')
        user = self.context.get('user')
        if password != password2:
            raise serializers.ValidationError("passwords does't match")
        user.set_password(password)
        user.save()
        return attrs


class UserPasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)

    class Meta:
        fields = ['email']

    def validate(self, attrs):
        email = attrs.get('email')
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.id))
            print('Encoded Uid', uid)
            token = PasswordResetTokenGenerator().make_token(user)
            print("password reset token :", token)
            link = 'http://localhost:3000/api/user/reset/' + uid + '/' + token
            print("password reset link", link)
            # Send Email
            return attrs
        else:
            raise serializers.ValidationError({'error': 'You are not a Registered User'})


class FinalPasswordResetSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=255, style={"input_type": "password"}, write_only=True)
    password2 = serializers.CharField(max_length=255, style={"input_type": "password"}, write_only=True)

    class Meta:
        fields = ['password', 'password2']

    def validate(self, attrs):
        try:
            password = attrs.get('password')
            password2 = attrs.get('password2')
            uid = self.context.get('uid')
            token = self.context.get('token')
            if password != password2:
                raise serializers.ValidationError("passwords does't match")
            id = smart_str(urlsafe_base64_decode(uid))
            user = User.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise serializers.ValidationError({"error": "Token is not valid or expired!"})
            user.set_password(password)
            user.save()
            return attrs
        except DjangoUnicodeDecodeError as identifier:
            PasswordResetTokenGenerator().check_token(user, token)
            raise serializers.ValidationError({"error": "Token is not valid or Expired!"})


class LogoutTokenSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    default_error_messages = {
        'bad_token': _('Token is invalid or expired')
    }

    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs

    def save(self, **kwargs):
        try:
            RefreshToken(self.token).blacklist()
        except TokenError:
            self.fail('bad_token')
