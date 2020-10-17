from django.contrib.auth.models import User
from rest_framework import viewsets, generics
try:
    from rest_framework.decorators import detail_route, list_route
    def action(detail=None, **kwargs):
        if detail:
            return detail_route(**kwargs)
        return list_route(**kwargs)
except ImportError:
    from rest_framework.decorators import action


from . import serializers



class UserViewset(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer

    @action(detail=False)
    def test_list_route_decorator(self, request):
        return

    @action(methods=['put'], detail=True)
    def test_detail_route_decorator(self, request):
        return


class CustomViewset(viewsets.ViewSet):
    def get_serializer_class(self, *args, **kwargs):
        return str

    def destroy(self, request, *args, **kwargs):
        pass

    @action(detail=False)
    def test_list_route_decorator(self, request):
        return

    @action(methods=['patch'], detail=True)
    def test_detail_route_decorator(self, request):
        return


class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
