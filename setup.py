from os import path
import codecs
from setuptools import setup

read = lambda filepath: codecs.open(filepath, 'r', 'utf-8').read()

setup(
    name='django-sorter',
    version=":versiontools:sorter:",
    description='A helper app for sorting objects in Django templates and '
                'generating links without modifying the views.',
    long_description=read(path.join(path.dirname(__file__), 'README.rst')),
    author='Jannis Leidel',
    author_email='jannis@leidel.info',
    license='BSD',
    url='http://github.com/jezdez/django-sorter/',
    packages=['sorter', 'sorter.templatetags'],
    package_data={
        'sorter': ['templates/**.html'],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
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
    setup_requires=[
        'versiontools >= 1.6',
    ],
    install_requires=[
        'django-appconf >= 0.4',
        'django-ttag >= 2.2',
        'urlobject == 0.5.1',
    ],
)
