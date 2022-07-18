from django_filters.rest_framework import FilterSet
from utils.filters import MultipleCharFilter
from bepro_statistics.models import PurposeType
from django.db.models import Q


class StatisticsFilterSet(FilterSet):
    statistic_type = MultipleCharFilter(field_name="statistic_type", distinct=True)
    purpose = MultipleCharFilter(method="filter_purpose", distinct=True)
    visibility = MultipleCharFilter(field_name="visibility", distinct=True)

    @staticmethod
    def filter_purpose(queryset, name, value):
        values = {int(val.strip()) for val in value.split(",") if val}
        filter_kwargs = {}
        if {PurposeType.TO_ROLE, PurposeType.TO_DEPARTMENT} == values:
            filter_kwargs = {Q(department__isnull=False) | Q(role__isnull=False)}
        elif PurposeType.TO_DEPARTMENT in values:
            filter_kwargs = {Q(department__isnull=False) & Q(role__isnull=True)}
        elif PurposeType.TO_ROLE in values:
            filter_kwargs = {Q(department__isnull=True) & Q(role__isnull=False)}
        return queryset.filter(*filter_kwargs)

    class Meta:
        fields = ['statistic_type', "purpose", "visibility"]
