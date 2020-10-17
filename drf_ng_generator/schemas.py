try:
    from rest_framework.schemas import is_list_view, is_custom_action
    from .coreapi.schemas import SchemaGenerator
    API_MODE = 'coreapi'
except ImportError:
    from rest_framework.schemas.coreapi import is_list_view, is_custom_action
    from .openapi.schemas import SchemaGenerator
    API_MODE = 'openapi'
