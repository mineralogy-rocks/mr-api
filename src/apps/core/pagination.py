# -*- coding: UTF-8 -*-
from rest_framework.pagination import CursorPagination
from rest_framework.pagination import _reverse_ordering

from .models.mineral import Mineral


class CustomCursorPagination(CursorPagination):
    """
    Custom paginator allows to use cursor pagination with Window function
    """

    def get_ordering(self, request, queryset, view):
        if request.query_params.get("q", None) is not None:
            return [
                "ordering",
            ]
        return super().get_ordering(request, queryset, view)

    def paginate_raw_queryset(self, queryset, request, view=None, query=None):
        """
        Customized pagination method which allows to use cursor pagination with Window function
        by wrapping the query in a raw query.
        """
        assert query is not None, (
            "'%s' should either include a `query` attribute, "
            "or override the `paginate_queryset()` method." % self.__class__.__name__
        )

        self.request = request
        self.page_size = self.get_page_size(request)
        if not self.page_size:
            return None

        self.base_url = request.build_absolute_uri()
        self.ordering = self.get_ordering(request, queryset, view)

        self.cursor = self.decode_cursor(request)
        if self.cursor is None:
            (offset, reverse, current_position) = (0, False, None)
        else:
            (offset, reverse, current_position) = self.cursor

        # Cursor pagination always enforces an ordering.
        if reverse:
            queryset = queryset.order_by(*_reverse_ordering(self.ordering))
        else:
            queryset = queryset.order_by(*self.ordering)

        filter, limit = "", ""

        # If we have a cursor with a fixed position then filter by that.
        if current_position is not None:
            order = self.ordering[0]
            is_reversed = order.startswith("-")
            order_attr = order.lstrip("-")

            # Test for: (cursor reversed) XOR (queryset reversed)
            if self.cursor.reverse != is_reversed:
                filter = " WHERE main_table.%s < '%s' " % (order_attr, current_position)
            else:
                filter = " WHERE main_table.%s > '%s' " % (order_attr, current_position)

        # If we have an offset cursor then offset the entire page by that amount.
        # We also always fetch an extra item in order to determine if there is a
        # page following on from this one.

        limit = " LIMIT %s OFFSET %s;" % (offset + self.page_size + 1, offset)

        sql, params = queryset.query.sql_with_params()
        _queryset = Mineral.objects.raw((query % sql) + filter + limit, params)
        results = list(_queryset)
        self.page = list(results[: self.page_size])

        # Determine the position of the final item following the page.
        if len(results) > len(self.page):
            has_following_position = True
            following_position = self._get_position_from_instance(results[-1], self.ordering)
        else:
            has_following_position = False
            following_position = None

        if reverse:
            # If we have a reverse queryset, then the query ordering was in reverse
            # so we need to reverse the items again before returning them to the user.
            self.page = list(reversed(self.page))

            # Determine next and previous positions for reverse cursors.
            self.has_next = (current_position is not None) or (offset > 0)
            self.has_previous = has_following_position
            if self.has_next:
                self.next_position = current_position
            if self.has_previous:
                self.previous_position = following_position
        else:
            # Determine next and previous positions for forward cursors.
            self.has_next = has_following_position
            self.has_previous = (current_position is not None) or (offset > 0)
            if self.has_next:
                self.next_position = following_position
            if self.has_previous:
                self.previous_position = current_position

        # Display page controls in the browsable API if there is more
        # than one page.
        if (self.has_previous or self.has_next) and self.template is not None:
            self.display_page_controls = True

        return self.page
