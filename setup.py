import os
from setuptools import setup

try:
    README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()
except:
    README = ''

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-rest-framework-angular-resource-generator',
    version='3.0.3',
    packages=['drf_ng_generator'],
    include_package_data=True,
    license='BSD License',
    description='Angular resource generator for DRF',
    long_description=README,
    author='Gerasev Kirill',
    author_email='gerasev.kirill@gmail.com',
    install_requires=[
        'Django>=1.10',
        'coreapi',
        'djangorestframework'
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
