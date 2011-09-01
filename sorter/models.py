from appconf import AppConf

class SorterConf(AppConf):
    RAISE_EXCEPTIONS = None
    QUERY_NAME = 'sort'
    EVALUATE_AFTERWARDS = True
    ALLOWED_ORDERING = None

    def configure_raise_exceptions(self, value):
        from django.conf import settings
        return settings.DEBUG

    def configure_allowed_ordering(self, value):
        """
        A mapping of sorter names and ordering names
        which should should be allowed. The ordering names
        support Unix shell-style wildcards, e.g. 'fieldname__*'.

        SORTER_ALLOWED_ORDERING = {
            'sort': ['*'],
            'sort_posts': ['name', 'author__username'],
        }
        """
        return value or {}
