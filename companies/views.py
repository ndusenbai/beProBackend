from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from companies.models import Company, Department
from companies.serializers import CompanyModelSerializer, DepartmentModelSerializer


class CompanyViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = CompanyModelSerializer
    queryset = Company.objects.order_by()


class DepartmentViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = DepartmentModelSerializer
    queryset = Department.objects.order_by()
