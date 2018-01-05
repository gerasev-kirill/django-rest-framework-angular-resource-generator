from django.test import TestCase, RequestFactory
from django.template.loader import render_to_string
from django.conf import settings
import os, json


from drf_ng_generator import schemas
from drf_ng_generator.converter import SchemaConverter
from drf_ng_generator.management.commands.drf_ng import Command


with open(os.path.join(settings.BASE_DIR, 'rest_schema.json')) as f:
    REST_SCHEMA = json.load(f)


class TestTemplate(TestCase):
    def get_schema(self):
        generator = schemas.SchemaGenerator()
        schema = generator.get_schema()
        converter = SchemaConverter()
        return converter.convert(schema)

    def __test(self, file_content):
        for modelName, conf in REST_SCHEMA.items():
            self.assertIn(
                '.factory("'+modelName+'"',
                file_content
            )
            for name, apiConf in conf['api'].items():
                self.assertIn(
                    '"'+apiConf['url']+'",',
                    file_content
                )


    def test_coffee(self):
        rest_schema, base_url = self.get_schema()

        coffee = render_to_string(
            'ngResource.coffee',
            {'API': rest_schema, 'API_URL_BASE': base_url}
        )
        self.__test(coffee)


    def test_js(self):
        rest_schema, base_url = self.get_schema()

        js = render_to_string(
            'ngResource.js',
            {'API': rest_schema, 'API_URL_BASE': base_url}
        )
        self.__test(js)


    def test_command(self):
        import tempfile
        fd, fpath = tempfile.mkstemp(suffix='.js')

        c = Command()
        c.handle(filepath=[fpath])
        with open(fpath) as fd:
            js = fd.read()

        self.__test(js)

        fd, fpath = tempfile.mkstemp(suffix='.coffee')

        c = Command()
        c.handle(filepath=[fpath])
        with open(fpath) as fd:
            coffee = fd.read()

        self.__test(coffee)
