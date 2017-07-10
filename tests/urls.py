from rest_framework import routers
from django.conf.urls import url, include
from rest_framework_swagger.views import get_swagger_view

schema_view = get_swagger_view(title='Site API')

urlpatterns = [
    url('^api/v1/', include('tests.rest.urls')),
    url(r'^docs/', schema_view)
]
