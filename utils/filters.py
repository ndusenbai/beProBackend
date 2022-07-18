from django_filters import CharFilter


class MultipleCharFilter(CharFilter):
    def filter(self, qs, value):
        if not value:
            return qs

        values = value.split(',')
        if len(values) > 1:
            self.lookup_expr = 'in'
        else:
            values = values[0]

        return super(MultipleCharFilter, self).filter(qs, values)
