# from django.shortcuts import render
import datetime

from rest_framework.pagination import PageNumberPagination
from .pagination import PaginationHandlerMixin
from django.db.models import Q
from rest_framework.generics import ListAPIView, GenericAPIView
from rest_framework.views import APIView
from user.models import Doctor,Slots,Patient
from rest_framework.response import Response
from rest_framework.views import status
from .serializers import DocDetailsSerializers,DocSpecialistSerializers,BookSlotSerializer,DashboardTableSerializer
from rest_framework.permissions import IsAuthenticated


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
        return Response({"success":"successful slot booking!"},status=status.HTTP_200_OK)

class DashboardTableView(APIView):

    permission_classes = [IsAuthenticated]
    serializer_class = DashboardTableSerializer

    def get(self, request, format=None):
        user = request.user
        tabletype = request.GET.get('tabletype')
        print(tabletype)
        if user.is_staff:
            mydoc = Doctor.objects.get(user=user)
            instance = Slots.objects.filter(doctor=mydoc, slot_selected__lt=datetime.datetime.now()).all()
            if tabletype=="f":
                instance = Slots.objects.filter(doctor=mydoc, slot_selected__gte=datetime.datetime.now()).all()

        else:
            mypat = Patient.objects.get(user=user)
            instance = Slots.objects.filter(patient=mypat, slot_selected__lt=datetime.datetime.now()).all()
            if tabletype == "f":
                instance = Slots.objects.filter(patient=mypat, slot_selected__gte=datetime.datetime.now()).all()

        sz = self.serializer_class(instance,many=True)

        return Response(sz.data, status=status.HTTP_200_OK)