from django.core.management.base import BaseCommand, CommandError
from django.template.loader import render_to_string

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

        coffee = render_to_string(
            'ngResource.coffee',
            {'API': converter.convert(schema)}
        )
        for fpath in options.get('filepath', []):
            with open(fpath, 'w') as f:
                f.write(coffee)
