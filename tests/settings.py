SITE_ID = 1

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.sites',
    'django.contrib.auth',
    'django.contrib.admin',
    'sorter',
    'sorter_tests',
]


SORTER_ALLOWED_CRITERIA = {
    'sort': ['*'],
    'sort_objects': ['*'],
    'sort1': ['*'],
    'sort2': ['*'],
    'sort_others': ['*'],
}
