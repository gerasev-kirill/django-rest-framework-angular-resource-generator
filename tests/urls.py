from rest_framework import routers
from django.conf.urls import url, include


urlpatterns = [
    url('^api/v1/', include('tests.rest.urls'))
]
