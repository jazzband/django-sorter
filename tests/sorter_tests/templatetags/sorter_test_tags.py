from django.template import Library

register = Library()

@register.filter
def pks(value):
    pk_list = []
    for obj in value:
        pk_list.append(str(obj.pk))
    if pk_list:
        return u'.'.join(pk_list)
    return ''
