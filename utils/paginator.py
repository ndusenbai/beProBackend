import sys
from functools import cached_property

from django.core.paginator import InvalidPage, Paginator
from django.db.models import Count
from rest_framework.exceptions import NotFound
from rest_framework_json_api.pagination import JsonApiPageNumberPagination


class CustomPaginator(Paginator):

    @cached_property
    def count(self):
        return self.object_list.aggregate(Count('id'))['id__count']


class PagePagination(JsonApiPageNumberPagination):
    max_page_size = sys.maxsize

    def paginate_queryset(self, queryset, request, view=None):
        """
                Paginate a queryset if required, either returning a
                page object, or `None` if pagination is not configured for this view.
                """
        page_size = self.get_page_size(request)
        if not page_size:
            return None

        paginator = CustomPaginator(queryset, page_size)
        page_number = self.get_page_number(request, paginator)

        try:
            self.page = paginator.page(page_number)
        except InvalidPage as exc:
            msg = self.invalid_page_message.format(
                page_number=page_number, message=str(exc)
            )
            raise NotFound(msg)

        if paginator.num_pages > 1 and self.template is not None:
            # The browsable API should display pagination controls.
            self.display_page_controls = True

        self.request = request
        return list(self.page)
