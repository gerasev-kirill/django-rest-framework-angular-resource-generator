from rest_framework import routers
from django.conf.urls import url, include
from . import viewsets

router = routers.SimpleRouter()
router.register(r'users', viewsets.UserViewset)
router.register(r'custom', viewsets.CustomViewset, 'Custom')

urlpatterns = [
    url('^userlist/$', viewsets.UserListView.as_view())
] + router.urls
