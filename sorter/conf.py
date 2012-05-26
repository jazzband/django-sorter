from django.conf import settings  # noqa
from django.core.exceptions import ImproperlyConfigured
from appconf import AppConf


class SorterConf(AppConf):
    DEFAULT_QUERY_NAME = 'sort'
    ALLOWED_CRITERIA = None

    def configure_ALLOWED_CRITERIA(self, value):
        if not value:
            raise ImproperlyConfigured("The SORTER_ALLOWED_CRITERIA "
                                       "setting is empty. Please set it.")
        for name, criteria in value.items():
            if not name:
                raise ImproperlyConfigured("The '%s' SORTER_ALLOWED_CRITERIA "
                                           "setting is empty. Please set it." %
                                           name)
        return value or {}
