# Command for django that generates AngularJS services, compatible with ngResource.$resource, that provide client-side representation of the models and remote methods in angular-application.


Приложение сделано под впечатлением от loopback.js и генератора ngResource-описания для него.

## Quick start

* install using pip:

```bash
	pip install git+https://github.com/gerasev-kirill/django-rest-framework-angular-resource-generator
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
или (для генерации coffee-script файла):
```bash
	python ./manage.py drf_ng ./path-to-my-static-dir/resources.coffee
```

## Описание

Приложение имеет только 1 команду: drf_ng, которая генерирует описание ngResource
на основе urlpatterns для django-rest-framework
Вывод поддерживается в js и coffee файлы.
Возможности:

* генерация js и coffee-файлов
* ngResource генерируются только для views от rest_framework и обычные django-views не поддерживаются.
* поддерживается система авторизации по токену от http://www.django-rest-framework.org/api-guide/authentication/#tokenauthentication. Для этого в одной из view должены быть определены такие методы:

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

и добавлено приложение rest_framework.authtoken, также установлена авторизация через токен:

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

после подключения viewset к router, например, 'user' мы можем вызывать в js такой код
для логина пользователя:


```js
angular.module('myModule')

.controller('MyController', function($scope, User){
	$scope.data = {
		username: '',
		password: ''
	};
	// если нужно чтоб логин пользователя длился больше чем сессия браузера, то
	// добавьте такое поле
	$scope.data.rememberMe = true;
	// rememberMe - влияет только на сервис djAuth

	$scope.login = function(){
		User.login($scope.data, function(data){
			// data = {token: '...', userId: 0}
			// теперь мы можем делать любые запросы к серверу, которые требуют авторизации
			// например:
			User.query();
			// и для этого не нужно нигде специально сохранять токен
		});
	};

	$scope.logout = function(){
		User.logout(function(){
			// теперь любой запрос к серверу, который требует авторизацию будет отклоняться
			// самим сервером.
		});
	}
});

```



Также доступен сервис djAuth, который содержит такие свойства:
	djAuth.accessTokenId,
	djAuth.currentUserId
эти переменные изменяются при логине/разлогине пользователя.

Вы можете также добавить метод register в ваш django viewset, который возвращает те же поля что и
login метод, и тогда можно регистрировать пользователей с помощью ангулоровских сервисов:

```js
	var data = {username: 'Hello', password: 'world!', email: 'mail@mail.com'};
	User.register(data, function(data){
		// data = {token: '...', userId: 1}
	});
```


Подробнее смотрите сгенерированный код js или coffee файла
