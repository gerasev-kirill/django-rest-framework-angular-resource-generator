from django.contrib.auth.models import User
from rest_framework import viewsets, generics
from rest_framework.decorators import detail_route, list_route


from . import serializers



class UserViewset(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer

    @list_route()
    def test_list_route_decorator(self, request):
        return

    @detail_route(methods=['put'])
    def test_detail_route_decorator(self, request):
        return


class CustomViewset(viewsets.ViewSet):
    def get_serializer_class(self, *args, **kwargs):
        return str

    def destroy(self, request, *args, **kwargs):
        pass

    @list_route()
    def test_list_route_decorator(self, request):
        return

    @detail_route(methods=['patch'])
    def test_detail_route_decorator(self, request):
        return


class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
