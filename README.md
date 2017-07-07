# Command for django that generates AngularJS services, compatible with ngResource.$resource, that provide client-side representation of the models and remote methods in angular-application.

App was inspired by loopback.js.

## Quick start

* install using pip:

```bash
    pip install django-rest-framework-angular-resource-generator
```

* add "drf_ng_generator" to your INSTALLED_APPS setting like this:

```python
INSTALLED_APPS = (
    ...
    'drf_ng_generator'
)
```

* run next command to create ngResource-file from drf views:

```bash
    python ./manage.py drf_ng ./path-to-my-static-dir/resources.js
```
or (to generate the coffee-script file):
```bash
    python ./manage.py drf_ng ./path-to-my-static-dir/resources.coffee
```

Example of generated services: [exampleResource.js](exampleResource.js)

## Description

The application has just one command - drf_ng, that is used to generate the ngResource description based on urlpatterns for django-rest-framework.
The output can be saved into js and coffee files.


Functionality:
* generating js and coffee-script files
* ngResource are being generated only for views from rest_framework, and general django-views are not supported.
* the authorization flow for token from http://www.django-rest-framework.org/api-guide/authentication/#tokenauthentication is supported. To implement this one of the views should contain the following methods defined :


```python
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

```


and the application rest_framework.authtoken should be added, and also the authorization through the token should be set as described below:

```python
INSTALLED_APPS = (
    ...
    'rest_framework.authtoken'
)
...
REST_FRAMEWORK = {
    ...
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    )
    ...
}
```


after viewset is connected to router, for example 'user', we can call the following code to log in the user:

```js
angular.module('myModule', ['djServices'])

.controller('MyController', function($scope, User){
    var params = {};
    $scope.data = {
        username: '',
        password: ''
    };
    // if needed to keep the user logged in for longer time then browser session, you can add the following field
    params.rememberMe = true;
    // rememberMe - impacts only the djAuth service

    $scope.login = function(){
        User.login(params, $scope.data, function(data){
            // data = {token: '...', userId: 0}
            // now we can make any calls to the server where authorization is required
            // for example
            User.query();
            // and we don't need to manage the storage of the token
        });
    };

    $scope.logout = function(){
        User.logout(function(){
            // now any request to the server that needs authorization will be rejected by the server
        });
    }
});

```


 Also the service djAuth is available, and contains the following properties:
djAuth.accessTokenId,
djAuth.currentUserId
These variables are being changed during user log in/ log off.

You can also add a method "register" to your django viewset, that returns same fields as the login method;
and therefore you can register users using angular services:

```js
    var data = {username: 'Hello', password: 'world!', email: 'mail@mail.com'};
    User.register(data, function(data){
        // data = {token: '...', userId: 1}
    });
```

Please review the generated js or coffee files code for more details
