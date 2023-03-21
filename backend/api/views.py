from django.shortcuts import render
from rest_framework.pagination import PageNumberPagination
from .pagination import PaginationHandlerMixin
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from user.models import Doctor
from rest_framework.response import Response
from rest_framework.views import status
from .serializers import DocDetailsSerializers
# Create your views here.
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 10

class DocDetailsView(APIView,PaginationHandlerMixin):
    pagination_class = StandardResultsSetPagination
    # queryset = Doctor.objects.filter(details_status=True).all()
    serializer_class = DocDetailsSerializers

    def get(self, request, format=None, *args, **kwargs):
        instance = Doctor.objects.filter(details_status=True).all()
        page = self.paginate_queryset(instance)
        if page is not None:
            serializer = self.get_paginated_response(self.serializer_class(page,
                                                                           many=True).data)
        else:
            serializer = self.serializer_class(instance, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)