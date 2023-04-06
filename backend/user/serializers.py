from xml.dom import ValidationErr
import datetime
from rest_framework import serializers
from .models import User, Doctor, Patient,Slots
from django.core.mail import send_mail

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


class ExtraDocDetailsSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20, write_only=True)
    qualification = serializers.CharField(max_length=200, write_only=True)
    speciality = serializers.CharField(max_length=200, write_only=True)
    hosp_name = serializers.CharField(max_length=200, write_only=True)
    experience = serializers.IntegerField(write_only=True)
    fees = serializers.IntegerField(write_only=True)
    slot_start = serializers.CharField(max_length=8, write_only=True)
    slot_end = serializers.CharField(max_length=8, write_only=True)
    age = serializers.IntegerField(write_only=True)
    gender = serializers.CharField(
        max_length=2,
        write_only=True
    )

    class Meta:
        fields = ['phone', 'qualification', 'speciality', 'hosp_name', 'experience', 'fees', 'slot_start', 'slot_end',
                  'age', 'gender']

    def validate(self, attrs):
        user = self.context.get('user')
        user.details_status = True
        user.save()
        doc = Doctor.objects.get(user=user)
        doc.phone = attrs.get('phone')
        doc.qualification = attrs.get('qualification')
        doc.speciality = attrs.get('speciality')
        doc.hosp_name = attrs.get('hosp_name')
        doc.experience = attrs.get('experience')
        doc.fees = attrs.get('fees')
        a = attrs.get('slot_start').split(":")
        print(a)
        c = attrs.get('slot_end').split(":")
        if len(a) and len(c) <= 2:
            raise serializers.ValidationError("Time input is invalid!")
        b = datetime.time(int(a[0]), int(a[1]), int(a[2]))
        d = datetime.time(int(c[0]), int(c[1]), int(c[2]))

        if type(b) and type(d) == datetime.time:
            doc.slot_start = b
            doc.slot_end = d
        else:
            raise serializers.ValidationError("Time input is invalid!")
        doc.age = attrs.get('age')
        doc.gender = attrs.get('gender')
        doc.details_status = True
        doc.save()
        return attrs


class ExtraPatDetailsSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20, write_only=True)
    age = serializers.IntegerField(write_only=True)
    gender = serializers.CharField(
        max_length=2,
        write_only=True
    )

    class Meta:
        fields = ['phone', 'age', 'gender']

    def validate(self, attrs):
        user = self.context.get('user')
        user.details_status = True
        user.save()
        pat = Patient.objects.get(user=user)
        pat.phone = attrs.get('phone')
        pat.age = attrs.get('age')
        pat.gender = attrs.get('gender')
        pat.details_status = True
        pat.save()
        return attrs


# class docSettingsListSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Doctor
#         fields = ['phone', 'qualification', 'speciality', 'hosp_name', 'experience', 'fees', 'slot_start', 'slot_end',
#                   'age', 'gender']
#


class UserLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255)

    class Meta:
        model = User
        fields = ['email', 'password']


class UserProfileSerializer(serializers.ModelSerializer):
    img = serializers.SerializerMethodField()
    count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'img','created_at','is_verified','is_staff','count']

    def get_img(self, instance: User):

        try:
            user = Doctor.objects.get(user=instance)
        except Doctor.DoesNotExist:
            user = Patient.objects.get(user=instance)
        return user.img

    def get_count(self,instance:User):
        count = set()
        try:
            user = Doctor.objects.get(user=instance)
            all_slots =Slots.objects.filter(doctor=user)
            for loop in all_slots:
                count.add(loop.patient.user.name)
            return len(count)


        except Doctor.DoesNotExist:
            user = Patient.objects.get(user=instance)
            all_slots = Slots.objects.filter(patient=user)
            for loop in all_slots:
                count.add(loop.patient.user.name)
            return len(count)
        # return .objects.filter(product_id=obj.id).count()


class DocSettingDetailsSerializers(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = ["user_id", "img", "phone", "qualification", "speciality", "hosp_name", "experience", "fees",
                  "slot_start",
                  "slot_end", "age", "gender"]


class PatSettingsDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ["img", 'phone', 'age', 'gender']


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
            raise serializers.ValidationError({"error":"passwords does't match"})
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
            link = 'http://localhost:3000/resetpass/' + uid + '/' + token
            print("password reset link", link)
            send_mail(
                'Here is Your Password Reset Link:',
                link,
                'fakeoffice007@gmail.com',
                [email],
                fail_silently=False,
            )
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
                raise serializers.ValidationError({"error": "passwords does't match"})
            id = smart_str(urlsafe_base64_decode(uid))
            user = User.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise serializers.ValidationError({"error": "Token is not valid or expired!"})
            user.set_password(password)
            user.save()
            RefreshToken(token).blacklist()
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
