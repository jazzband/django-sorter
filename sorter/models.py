from appconf import AppConf

class SorterConf(AppConf):
    DEFAULT_QUERY_NAME = 'sort'
    ALLOWED_CRITERIA = None

    def configure_ALLOWED_CRITERIA(self, value):
        return value or {}
