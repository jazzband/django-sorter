from appconf import AppConf

class SorterConf(AppConf):
    RAISE_EXCEPTIONS = None
    QUERY_NAME = 'sort'
    EVALUATE_AFTERWARDS = True

    def configure_raise_exceptions(self, value):
        from django.conf import settings
        return settings.DEBUG
