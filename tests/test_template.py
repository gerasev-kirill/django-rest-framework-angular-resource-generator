from django.test import TestCase, RequestFactory
from django.template.loader import render_to_string
from django.conf import settings
import os, json


from drf_ng_generator import schemas
from drf_ng_generator.converter import SchemaConverter


with open(os.path.join(settings.BASE_DIR, 'rest_schema.json')) as f:
    REST_SCHEMA = json.load(f)


class TestTemplate(TestCase):
    def get_schema(self):
        generator = schemas.SchemaGenerator()
        schema = generator.get_schema()
        converter = SchemaConverter()
        return converter.convert(schema)

    def test_coffee(self):
        rest_schema = self.get_schema()

        coffee = render_to_string(
            'ngResource.coffee',
            {'API': rest_schema}
        )
        for modelName, conf in REST_SCHEMA.items():
            self.assertIn(
                '.factory("'+modelName+'"',
                coffee
            )
            for name, apiConf in conf['api'].items():
                self.assertIn(
                    '"'+apiConf['url']+'",',
                    coffee
                )

    def test_js(self):
        rest_schema = self.get_schema()

        js = render_to_string(
            'ngResource.js',
            {'API': rest_schema}
        )

        for modelName, conf in REST_SCHEMA.items():
            self.assertIn(
                '.factory("'+modelName+'"',
                js
            )
            for name, apiConf in conf['api'].items():
                self.assertIn(
                    '"'+apiConf['url']+'",',
                    js
                )
