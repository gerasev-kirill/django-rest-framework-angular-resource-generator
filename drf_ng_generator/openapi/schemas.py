import warnings
from urllib.parse import urljoin
from rest_framework.schemas.openapi import SchemaGenerator as BaseSchemaGenerator


KNOWN_REST_POINTS = {
    'list': 'get',
    'retrieve': 'get',
    'update': 'put',
    'partial_update': 'patch',
    'destroy': 'delete'
}

class SchemaGenerator(BaseSchemaGenerator):
    def _get_paths_and_endpoints(self, request):
        """
        Generate (path, method, view) given (path, method, callback) for paths.
        """
        paths = []
        view_endpoints = []
        for path, method, callback in self.endpoints:
            if not hasattr(callback, 'actions'):
                func_name = None
                view = self.create_view(callback, method, request)
                for k in KNOWN_REST_POINTS:
                    if hasattr(view, k):
                        func_name = k
                        break
                if not func_name:
                    continue
            else:
                func_name = callback.actions[method.lower()]
            view = self.create_view(callback, method, request)
            path = self.coerce_path(path, method, view)
            paths.append(path)
            view_endpoints.append((path, method, view, func_name))

        return paths, view_endpoints


    def check_duplicate_operation_id(self, *args, **kwargs):
        # подавляем дебильный вывод варнингов о дубликатах, т.к. они не имеют смысла
        pass


    def get_schema(self, request=None, public=False):
        """
        Generate a OpenAPI schema.
        """
        self._initialise_endpoints()
        components_schemas = {}

        # Iterate endpoints generating per method path operations.
        paths = {}
        _, view_endpoints = self._get_paths_and_endpoints(None if public else request)
        for path, method, view, func_name in view_endpoints:
            if not self.has_view_permissions(path, method, view):
                continue

            operation = view.schema.get_operation(path, method)
            operation['x-django'] = {
                'view': view,
                'function': func_name
            }
            components = view.schema.get_components(path, method)
            for k in components.keys():
                if k not in components_schemas:
                    continue
                if components_schemas[k] == components[k]:
                    continue
                warnings.warn('Schema component "{}" has been overriden with a different value.'.format(k))

            components_schemas.update(components)

            # Normalise path for any provided mount url.
            if path.startswith('/'):
                path = path[1:]
            path = urljoin(self.url or '/', path)

            paths.setdefault(path, {})
            paths[path][method.lower()] = operation

        self.check_duplicate_operation_id(paths)

        # Compile final schema.
        schema = {
            'openapi': '3.0.2',
            'info': self.get_info(),
            'paths': paths,
        }

        if len(components_schemas) > 0:
            schema['components'] = {
                'schemas': components_schemas
            }

        return schema
