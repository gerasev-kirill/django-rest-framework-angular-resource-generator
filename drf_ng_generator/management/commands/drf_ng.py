from django.core.management.base import BaseCommand, CommandError
from django.template.loader import render_to_string
from django.conf import settings
import os

from drf_ng_generator import schemas
from drf_ng_generator.converter import SchemaConverter




class Command(BaseCommand):
    help = ''
    def add_arguments(self, parser):
        parser.add_argument('filepath', nargs='+', type=str)

    def handle(self, *args, **options):
        generator = schemas.SchemaGenerator()
        schema = generator.get_schema()
        if not schema:
            return
        converter = SchemaConverter()

        for fpath in options.get('filepath', []):
            ext = os.path.splitext(fpath)[-1].lower()
            if ext not in ['.coffee', '.js']:
                fpath += '.js'
                ext = '.js'
            app_api, api_url_base = converter.convert(schema, order=True, ignore_viewset_names=True)
            prefix = getattr(settings, 'DRFGEN_SERVICE_PREFIX_NAME', None) or getattr(settings, 'DRF_GENERATOR_SERVICE_PREFIX_NAME', None) or 'dj'
            resources = render_to_string(
                'ngResource'+ext,
                {
                    'API': app_api,
                    'API_URL_BASE': api_url_base,
                    'SERVICE_PREFIX_NAME': prefix
                }
            )
            with open(fpath, 'w') as f:
                f.write(resources)
