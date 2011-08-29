from django.conf import settings
from appconf import AppConf

class SorterConf(AppConf):
    RAISE_EXCEPTIONS = settings.DEBUG
    QUERY_NAME = 'sort'
