# from django.shortcuts import render
from rest_framework.pagination import PageNumberPagination
from .pagination import PaginationHandlerMixin
from django.db.models import Q
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from user.models import Doctor
from rest_framework.response import Response
from rest_framework.views import status
from .serializers import DocDetailsSerializers,DocSpecialistSerializers


# Create your views here.
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 1
    page_size_query_param = 'page_size'
    max_page_size = 1


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
