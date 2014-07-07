import os
import codecs
import re
from setuptools import setup
from sorter import __version__ as VERSION


def read(*parts):
    return codecs.open(os.path.join(os.path.dirname(__file__), *parts)).read()


setup(
    name='django-sorter',
    version=VERSION,
    description='A helper app for sorting objects in Django templates.',
    long_description=read('README.rst'),
    author='Jannis Leidel',
    author_email='jannis@leidel.info',
    license='BSD',
    url='http://django-sorter.readthedocs.org/',
    packages=['sorter', 'sorter.templatetags'],
    package_data={
        'sorter': [
            'templates/sorter/*.html',
            'locale/*/*/*',
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Utilities',
    ],
    install_requires=[
        'django-appconf >= 0.4',
        'django-ttag >= 2.3',
        'URLObject >= 2.0.1',
    ],
)
