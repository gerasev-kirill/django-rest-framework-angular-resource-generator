from django.test import TestCase

from drf_ng_generator import schemas, helpers
from drf_ng_generator.converter import SchemaConverter
from .rest.viewsets import UserViewset




class TestGenerator(TestCase):
    def setUp(self):
        self.maxDiff = None

    def test_helpers_resolve(self):
        generator = schemas.SchemaGenerator()
        schema = generator.get_schema()
        converter = SchemaConverter()
        rest_schema, api_url_base = converter.convert(schema)

        if schemas.API_MODE == 'coreapi':
            cb, raw_url, method = helpers.resolve_api_callback_by_name(rest_schema, 'users', 'list')
        else:
            cb, raw_url, method = helpers.resolve_api_callback_by_name(rest_schema, 'User', 'list')
        original_cb = UserViewset.as_view({'get': 'list'})

        self.assertEqual(method, 'get')
        # check by function code
        self.assertEqual(
            cb.__code__.co_code,
            original_cb.__code__.co_code
        )
        if schemas.API_MODE == 'coreapi':
            cb, raw_url, method = helpers.resolve_api_callback_by_name(rest_schema, 'users', 'testListRouteDecorator')
        else:
            cb, raw_url, method = helpers.resolve_api_callback_by_name(rest_schema, 'User', 'testListRouteDecorator')
        original_cb = UserViewset.as_view({'get': 'test_list_route_decorator'})

        self.assertEqual(method, 'get')
        # check by function code
        self.assertEqual(
            cb.__code__.co_code,
            original_cb.__code__.co_code
        )


        cb, raw_url, method = helpers.resolve_api_callback_by_name(rest_schema, 'users', 'Nomethod')
        self.assertEqual(cb, None)
        cb, raw_url, method = helpers.resolve_api_callback_by_name(rest_schema, 'Nopoint', 'Nomethod')
        self.assertEqual(cb, None)
