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
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': (
                "django.contrib.auth.context_processors.auth",
            ),
            'builtins': [
                'sorter.templatetags.sorter_tags',
                'sorter.tests',
            ]
        },
    },
]

SECRET_KEY = 'something-something'
