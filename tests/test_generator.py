from django.test import TestCase, RequestFactory
from django.conf import settings
import json, os

from drf_ng_generator import schemas, helpers
from drf_ng_generator.converter import SchemaConverter



with open(os.path.join(settings.BASE_DIR, 'rest_schema.{mode}.json'.format(mode=schemas.API_MODE))) as f:
    REST_SCHEMA = json.load(f)


class TestGenerator(TestCase):
    def setUp(self):
        self.maxDiff = None

    def test_generator(self):
        generator = schemas.SchemaGenerator()
        schema = generator.get_schema()
        converter = SchemaConverter()
        rest_schema, api_url_base = converter.convert(schema, ignore_viewset_names=True)
        rest_schema = json.loads(
            helpers.dumps_api_doc(rest_schema)
        )

        self.assertEqual(api_url_base, '/api/v1')
        self.assertDictEqual(
            rest_schema,
            REST_SCHEMA
        )
