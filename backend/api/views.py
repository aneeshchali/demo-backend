# from django.shortcuts import render
import datetime

from rest_framework.pagination import PageNumberPagination
from .pagination import PaginationHandlerMixin
from django.db.models import Q
from rest_framework.generics import ListAPIView, GenericAPIView
from rest_framework.views import APIView
from user.models import Doctor, Slots, Patient
from rest_framework.response import Response
from rest_framework.views import status
from .serializers import DocDetailsSerializers, DocSpecialistSerializers, BookSlotSerializer, DashboardTableSerializer, \
    ConnectCallSerializer, PrescriptionSerializer, DoctorSlotCheckSerializer
from rest_framework.permissions import IsAuthenticated
import datetime
import json



# Create your views here.
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 10


class DocDetailsView(APIView, PaginationHandlerMixin):
    pagination_class = StandardResultsSetPagination
    serializer_class = DocDetailsSerializers

    def get(self, request, format=None, *args, **kwargs):
        search = request.GET.get('search')
        l = request.GET.get('l').split(',')
        s = request.GET.get('s')
        if l[0] == "":
            if s:
                if s == "fasc":
                    instance = Doctor.objects.filter(Q(details_status=True) & Q(admin_verified=True) & Q(
                        user__name__icontains=search)).order_by('-fees').all()
                elif s == "fdes":
                    instance = Doctor.objects.filter(Q(details_status=True) & Q(admin_verified=True) & Q(
                        user__name__icontains=search)).order_by('fees').all()
                elif s == "Female":
                    instance = Doctor.objects.filter(Q(details_status=True) & Q(admin_verified=True) & Q(
                        user__name__icontains=search) & Q(gender__exact="F")).all()
                elif s == "Male":
                    instance = Doctor.objects.filter(Q(details_status=True) & Q(admin_verified=True) & Q(
                        user__name__icontains=search) & Q(gender__exact="M")).all()
                else:
                    instance = Doctor.objects.filter(Q(details_status=True) & Q(admin_verified=True) & Q(
                        user__name__icontains=search)).all()
            else:
                instance = Doctor.objects.filter(Q(details_status=True) & Q(admin_verified=True) & Q(
                    user__name__icontains=search)).all()
        else:
            if s:
                if s == "fasc":
                    instance = Doctor.objects.filter(
                        Q(details_status=True) & Q(admin_verified=True) & Q(speciality__in=l) & Q(
                            user__name__icontains=search)).order_by('-fees').all()
                elif s == "fdes":
                    instance = Doctor.objects.filter(
                        Q(details_status=True) & Q(admin_verified=True) & Q(speciality__in=l) & Q(
                            user__name__icontains=search)).order_by('fees').all()
                elif s == "Female":
                    instance = Doctor.objects.filter(
                        Q(details_status=True) & Q(admin_verified=True) & Q(speciality__in=l) & Q(
                            user__name__icontains=search) & Q(gender__exact="F")).all()
                elif s == "Male":
                    instance = Doctor.objects.filter(
                        Q(details_status=True) & Q(admin_verified=True) & Q(speciality__in=l) & Q(
                            user__name__icontains=search) & Q(gender__exact="M")).all()
                else:
                    instance = Doctor.objects.filter(
                        Q(details_status=True) & Q(admin_verified=True) & Q(speciality__in=l) & Q(
                            user__name__icontains=search)).all()
            else:
                instance = Doctor.objects.filter(
                    Q(details_status=True) & Q(admin_verified=True) & Q(speciality__in=l) & Q(
                        user__name__icontains=search)).all()
        page = self.paginate_queryset(instance)
        if page is not None:
            serializer = self.get_paginated_response(self.serializer_class(page,
                                                                           many=True).data)
        else:
            serializer = self.serializer_class(instance, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DocSpecialityView(ListAPIView):
    queryset = Doctor.objects.filter(details_status=True).all()
    serializer_class = DocSpecialistSerializers


class SlotBookingView(GenericAPIView):
    serializer_class = BookSlotSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args):
        print(request.data)
        sz = self.get_serializer(data=request.data, context={'patient': request.user})
        sz.is_valid(raise_exception=True)
        return Response({"success": "successful slot booking!"}, status=status.HTTP_200_OK)


class DashboardTableView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DashboardTableSerializer

    def get(self, request, format=None):
        user = request.user
        tabletype = request.GET.get('tabletype')
        print(tabletype)
        if user.is_staff:
            mydoc = Doctor.objects.get(user=user)
            instance = Slots.objects.filter(doctor=mydoc, slot_end_time__lt=datetime.datetime.now()).all()
            if tabletype == "f":
                instance = Slots.objects.filter(doctor=mydoc, slot_end_time__gte=datetime.datetime.now()).all()

        else:
            mypat = Patient.objects.get(user=user)
            instance = Slots.objects.filter(patient=mypat, slot_end_time__lt=datetime.datetime.now()).all()
            if tabletype == "f":
                instance = Slots.objects.filter(patient=mypat, slot_end_time__gte=datetime.datetime.now()).all()

        sz = self.serializer_class(instance, many=True)

        return Response(sz.data, status=status.HTTP_200_OK)


class ConnectCallView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ConnectCallSerializer

    def post(self, request, format=None):
        data = request.data
        slot = Slots.objects.get(id=data['data'])
        slot_time = slot.slot_selected
        slot_time = slot_time.strftime("%d/%m/%Y %H:%M:%S")
        slot_end_time = slot.slot_end_time
        slot_end_time = slot_end_time.strftime("%d/%m/%Y %H:%M:%S")
        # print(timezone.localtime() < slot_end_time)
        # print(timezone.localtime())
        # print(slot_end_time)
        a = datetime.datetime.now()
        checkTime = a.astimezone().strftime("%d/%m/%Y %H:%M:%S")
        # print(slot_time.strftime("%d/%m/%Y %H:%M:%S"))
        # print(a.astimezone().strftime("%d/%m/%Y %H:%M:%S"))
        # print(a.astimezone().strftime("%d/%m/%Y %H:%M:%S") > slot_time.strftime("%d/%m/%Y %H:%M:%S"))
        # end_slot_time = slot_time + datetime.timedelta(minutes=45)
        if slot_time <= checkTime <= slot_end_time:
            sz = self.serializer_class(slot)
            return Response(sz.data, status=status.HTTP_200_OK)
        elif slot_time > checkTime:
            return Response({"message": "It looks like we still have some time before the scheduled meeting."},
                            status=status.HTTP_400_BAD_REQUEST)
        elif slot_end_time <= checkTime:
            return Response({"message": "It looks like we passed the time for the scheduled meeting."},
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            sz = self.serializer_class(slot, many=True)
            return Response(sz.data, status=status.HTTP_200_OK)


class PrescriptionAddView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PrescriptionSerializer

    def post(self, request, format=None):
        data = request.data['data']
        slots = Slots.objects.get(id=data['id'])
        slots.prescription = data['text']
        slots.save()
        return Response({"message": "Success!"}, status=status.HTTP_200_OK)


class DoctorSlotCheckView(APIView):
    serializer_class = DoctorSlotCheckSerializer

    def get(self, request, format=None):
        setaDate = set()
        instance = Slots.objects.filter(doctor_id=10)
        sz = self.serializer_class(instance, many=True)
        print(len(instance))
        for loop in instance:
            print(loop.slot_selected)
            
        # a = json.loads(json.dumps(sz.data))
        return Response(sz.data, status=status.HTTP_200_OK)
