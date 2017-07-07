Command for django that generates AngularJS services, compatible with ngResource.$resource, that provide client-side representation of the models and remote methods in angular-application.
============================================================================================================================================================================================

.. |Build Status| image:: https://travis-ci.org/gerasev-kirill/django-rest-framework-angular-resource-generator.svg?branch=master
   :target: https://travis-ci.org/gerasev-kirill/django-rest-framework-angular-resource-generator
.. |Coverage Status| image:: https://coveralls.io/repos/github/gerasev-kirill/django-rest-framework-angular-resource-generator/badge.svg?branch=master
   :target: https://coveralls.io/github/gerasev-kirill/django-rest-framework-angular-resource-generator?branch=master

App was inspired by loopback.js.

Quick start
-----------

-  install using pip:

.. code:: bash

        pip install django-rest-framework-angular-resource-generator

-  add “drf\_ng\_generator” to your INSTALLED\_APPS setting like this:

.. code:: python

    INSTALLED_APPS = (
        ...
        'drf_ng_generator'
    )

-  run next command to create ngResource-file from drf views:

.. code:: bash

        python ./manage.py drf_ng ./path-to-my-static-dir/resources.js

or (to generate the coffee-script file):

.. code:: bash

        python ./manage.py drf_ng ./path-to-my-static-dir/resources.coffee


Example of generated services: `exampleResource.js`_
.. _exampleResource.js: exampleResource.js


Description
-----------

The application has just one command - drf\_ng, that is used to generate
the ngResource description based on urlpatterns for
django-rest-framework. The output can be saved into js and coffee files.

Functionality: \* generating js and coffee-script files \* ngResource
are being generated only for views from rest\_framework, and general
django-views are not supported. \* the authorization flow for token from
http://www.django-rest-framework.org/api-guide/authentication/#tokenauthentication
is supported. To implement this one of the views should contain the
following methods defined :

.. code:: python

    from django.contrib.auth.models import User

    from rest_framework.viewsets import ModelViewSet
    from rest_framework.decorators import list_route
    from rest_framework.authtoken import serializers
    from rest_framework.authtoken.models import Token
    from rest_framework.authentication import TokenAuthentication

    class UserViewset(ModelViewSet):
        queryset = User.objects.all()
        serializer_class = MyUserSerializer

        @list_route(methods=['post'])
        def login(self, request, *args, **kwargs):
            serializer = serializers.AuthTokenSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'userId': user.id
            })

        @list_route(methods=['delete'])
        def logout(self, request, *args, **kwargs):
            tAuth = TokenAuthentication()
            user, token = tAuth.authenticate(request)
            token.delete()
            return Response({}, status=204)

and the application rest\_framework.au
