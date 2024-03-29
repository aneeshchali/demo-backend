from rest_framework import serializers
import datetime
import math
import string
import random
import jwt
from django.core.mail import send_mail,EmailMessage
from django.template.loader import render_to_string
from user.models import Doctor, User, Slots, Patient
import razorpay
client = razorpay.Client(auth=("rzp_test_KEzRBHQhq8DEqj", "XHVZTmqLNWIXIubrIZ26SZGY"))
N = 15


class DocDetailsSerializers(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = Doctor
        fields = ["user", "img", "phone", "user_name", "qualification", "speciality", "hosp_name", "experience", "fees",
                  "slot_start",
                  "slot_end", "age", "gender"]

    def get_user_name(self, obj):
        return obj.user.name

class DashboardTableSerializer(serializers.ModelSerializer):

    doc_name = serializers.SerializerMethodField()
    pat_name = serializers.SerializerMethodField()

    class Meta:
        model = Slots
        fields = ["id","slot_selected","doc_name","pat_name","doctor","patient","prescription_status","prescription"]

    def get_doc_name(self, obj):
        return obj.doctor.user.name

    def get_pat_name(self, obj):
        return obj.patient.user.name


class ConnectCallSerializer(serializers.ModelSerializer):

    class Meta:
        model = Slots
        fields = ["id","video_id","video_cred"]



class DocSpecialistSerializers(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = ["speciality"]


class BookSlotSerializer(serializers.Serializer):
    date_time = serializers.CharField(max_length=200)
    doctor_id = serializers.CharField(max_length=200)
    order_id = serializers.CharField(max_length=200)


    class Meta:
        fields = ['date_time', 'doctor_id','order_id']

    def validate(self, attrs):
        patient = self.context.get('patient')
        date_time = attrs.get('date_time')
        order_id = attrs.get('order_id')
        date_time = datetime.datetime.strptime(date_time, "%d-%m-%Y %I:%M %p")
        date_time_end = date_time+datetime.timedelta(minutes=45)
        doctor_id = attrs.get('doctor_id')
        # return attrs
        if date_time<datetime.datetime.now():
            raise serializers.ValidationError({'error': 'Uh oh!, This is a old time slot!'})

        if Slots.objects.filter(slot_selected=date_time).exists():
            raise serializers.ValidationError({'error': 'Uh oh!, This slot is already booked.'})
        else:

            VIDEOSDK_API_KEY = "c24cd584-1bdd-4b8a-b59c-72e94e0eb715"
            VIDEOSDK_SECRET_KEY = "a23bbd666418c6cfc51202ca48f94e553cff0aa5b1d473bee3fb52ee429fde83"

            calculation = datetime.datetime.now() - (date_time+datetime.timedelta(minutes=45))
            expiration_in_seconds = math.ceil(calculation.total_seconds())
            expiration = datetime.datetime.now() + datetime.timedelta(seconds=expiration_in_seconds)

            token = jwt.encode(payload={
                'exp': expiration,
                'apikey': VIDEOSDK_API_KEY,
                'permissions': ['allow_join', 'allow_mod'],
            }, key=VIDEOSDK_SECRET_KEY, algorithm='HS256')
            # print(token)
            res = ''.join(random.choices(string.ascii_uppercase, k=N))
            doctor = Doctor.objects.get(user_id=doctor_id)
            patient = Patient.objects.get(user=patient)
            Slots.objects.create(doctor=doctor, patient=patient,order_id=order_id,slot_end_time=date_time_end, video_id=res, video_cred=token, slot_selected=date_time)
            return attrs


class FinalPaymentSerializer(serializers.Serializer):
    status = serializers.CharField(max_length=1)
    order_id = serializers.CharField(max_length=1000)
    payment_id = serializers.CharField(max_length=1000)


    class Meta:
        fields = ['order_id','payment_id','status']

    def validate(self, attrs):
        status = attrs.get('status')
        if status == 'p':
            order_id = attrs.get('order_id')
            payment_id = attrs.get('payment_id')
            updateInstance = Slots.objects.get(order_id=order_id)
            print(updateInstance)
            updateInstance.payment_id = payment_id
            updateInstance.payment_status = True
            updateInstance.save()

            #send mail to both the parties
            subject = 'Slot Booking Done'
            to = updateInstance.doctor.user.email
            from_email = 'chali.aneesh@gmail.com'
            template_name = 'slot_book.html'
            context = {'user': updateInstance.doctor.user.name, 'doctor': updateInstance.doctor.user.name,
                       'patient': updateInstance.patient.user.name, 'time': updateInstance.slot_selected}
            html_content = render_to_string(template_name, context)
            message = EmailMessage(subject, html_content, from_email, [to])
            message.content_subtype = "html"
            message.send()

            return attrs
        else:
            order_id = attrs.get('order_id')
            deleteInstance = Slots.objects.get(order_id=order_id)
            deleteInstance.delete()
            raise serializers.ValidationError({"error":"error"})
            return attrs





class PrescriptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Slots
        fields = ["prescription"]

# class DoctorSlotCheckSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Slots
#         fields = ["slot_selected"]
#
