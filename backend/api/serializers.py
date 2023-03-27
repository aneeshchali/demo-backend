from rest_framework import serializers
import datetime
import math
import string
import random

N = 15

import jwt

from user.models import Doctor, User, Slots, Patient


class DocDetailsSerializers(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = Doctor
        fields = ["user", "img", "phone", "user_name", "qualification", "speciality", "hosp_name", "experience", "fees",
                  "slot_start",
                  "slot_end", "age", "gender"]

    def get_user_name(self, obj):
        return obj.user.name


class DocSpecialistSerializers(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = ["speciality"]


class BookSlotSerializer(serializers.Serializer):
    date_time = serializers.CharField(max_length=200)
    doctor_id = serializers.CharField(max_length=200)

    class Meta:
        fields = ['date_time', 'doctor_id']

    def validate(self, attrs):
        patient = self.context.get('patient')
        date_time = attrs.get('date_time')
        date_time = datetime.datetime.strptime(date_time, "%d-%m-%Y %I:%M %p")
        doctor_id = attrs.get('doctor_id')
        # return attrs
        if Slots.objects.filter(slot_selected=date_time).exists():
            raise serializers.ValidationError({'error': 'Uh oh!, This slot is not empty.'})
        else:

            VIDEOSDK_API_KEY = "c24cd584-1bdd-4b8a-b59c-72e94e0eb715"
            VIDEOSDK_SECRET_KEY = "a23bbd666418c6cfc51202ca48f94e553cff0aa5b1d473bee3fb52ee429fde83"

            calculation = datetime.datetime.now() - date_time
            expiration_in_seconds = math.ceil(calculation.total_seconds())
            expiration = datetime.datetime.now() + datetime.timedelta(seconds=expiration_in_seconds)

            token = jwt.encode(payload={
                'exp': expiration,
                'apikey': VIDEOSDK_API_KEY,
                'permissions': ['allow_join', 'allow_mod'],
            }, key=VIDEOSDK_SECRET_KEY, algorithm='HS256')
            print(token)
            res = ''.join(random.choices(string.ascii_uppercase, k=N))
            doctor = Doctor.objects.get(user_id=doctor_id)
            patient = Patient.objects.get(user=patient)
            Slots.objects.create(doctor=doctor, patient=patient, video_id=res, video_cred=token, slot_selected=date_time)
            return attrs
