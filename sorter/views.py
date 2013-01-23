from utils import ordering

class Ordered(object):
    """Generic mixin view for ordering a queryset.
    """

    # Name of the order criteria, from settings, that will be used to sort the queryset
    order_by_criteria = None

    def get_order_by_criteria(self, queryset):
        return self.order_by_criteria

    def order_queryset(self, queryset, order_by_criteria):
        order_by = ordering(self.request, order_by_criteria)
        if order_by:
            return queryset.order_by(*order_by)
        return queryset

    def get_context_data(self, **kwargs):
        queryset = kwargs.pop('object_list')
        order_by_criteria = self.get_order_by_criteria(queryset)
        if order_by_criteria:
            context = {
                'is_ordered': True,
                'object_list': self.order_queryset(queryset, order_by_criteria)
            }
        else:
            context = {
                'is_ordered': False,
                'object_list': queryset
            }

        context.update(kwargs)

        return super(Ordered, self).get_context_data(**context)
