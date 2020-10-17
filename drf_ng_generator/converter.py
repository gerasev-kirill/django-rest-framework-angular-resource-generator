try:
    from rest_framework.schemas import is_list_view, is_custom_action
    from .coreapi.converter import SchemaConverter
except ImportError:
    from rest_framework.schemas.coreapi import is_list_view, is_custom_action
    from .openapi.converter import SchemaConverter
