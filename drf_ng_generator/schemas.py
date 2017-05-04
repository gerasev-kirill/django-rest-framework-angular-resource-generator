from rest_framework import schemas
from django.core.urlresolvers import RegexURLPattern, RegexURLResolver
import django



if django.VERSION[0] == 1 and django.VERSION[1] >= 10:
    class SchemaGenerator(schemas.SchemaGenerator):
        known_actions = (
            'create', 'read', 'retrieve', 'list',
            'update', 'partial_update', 'destroy',
            'GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'
        )
else:
    class SchemaGenerator(schemas.SchemaGenerator):

        def get_api_endpoints(self, patterns, prefix=''):
            """
            Return a list of all available API endpoints by inspecting the URL conf.
            """
            api_endpoints = []

            for pattern in patterns:
                path_regex = prefix + pattern.regex.pattern

                if isinstance(pattern, RegexURLPattern):
                    path = self.get_path(path_regex)
                    callback = pattern.callback
                    if self.should_include_endpoint(path, callback):
                        for method in self.get_allowed_methods(callback):
                            key = self.get_key(path, method, callback)
                            if key[0] == key[1]:
                                p = path.strip('/').split('/')
                                key = (
                                    p[-2],
                                    p[-1]
                                )
                            link = self.get_link(path, method, callback)
                            endpoint = (key, link, callback)
                            api_endpoints.append(endpoint)

                elif isinstance(pattern, RegexURLResolver):
                    nested_endpoints = self.get_api_endpoints(
                        patterns=pattern.url_patterns,
                        prefix=path_regex
                    )
                    api_endpoints.extend(nested_endpoints)

            return api_endpoints
