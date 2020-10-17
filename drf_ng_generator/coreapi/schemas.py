# DEPRECATED!

from rest_framework import schemas
import coreapi
from collections import OrderedDict

from .. import helpers

from rest_framework.schemas import is_list_view, is_custom_action



def insert_into(target, keys, value):
    """
    Nested dictionary insertion.

    >>> example = {}
    >>> insert_into(example, ['a', 'b', 'c'], 123)
    >>> example
    {'a': {'b': {'c': 123}}}
    """
    for key in keys[:-1]:
        if key not in target:
            target[key] = {}
        if not isinstance(target[key], coreapi.Link):
            target = target[key]
    target[keys[-1]] = value


class SchemaGenerator(schemas.SchemaGenerator):
    known_actions = (
        'create', 'read', 'retrieve', 'list',
        'update', 'partial_update', 'destroy',
        'GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'
    )
    def __init__(self, *args, **kwargs):
        if not kwargs.get('title', None):
            kwargs['title'] = 'AngularJs'
        super(SchemaGenerator, self).__init__(*args, **kwargs)


    def get_links(self, request=None):
        """
        Return a dictionary containing all the links that should be
        included in the API schema.
        """
        links = OrderedDict()

        # Generate (path, method, view) given (path, method, callback).
        paths = []
        view_endpoints = []
        for path, method, callback in self.endpoints:
            view = self.create_view(callback, method, request)
            if getattr(view, 'exclude_from_schema', False):
                continue
            path = self.coerce_path(path, method, view)
            paths.append(path)
            view_endpoints.append((path, method, view))

        # Only generate the path prefix for paths that will be included
        if not paths:
            return None
        prefix = self.determine_path_prefix(paths)

        for path, method, view in view_endpoints:
            if not self.has_view_permissions(path, method, view):
                continue
            link = self.get_link(path, method, view)
            subpath = path[len(prefix):]
            keys = self.get_keys(subpath, method, view)
            insert_into(links, keys, link)
        return links


    def get_link(self, path, method, view):
        link = super(SchemaGenerator, self).get_link(path, method, view)
        link._view = view
        return link


    def get_key(self, path, method, callback):
        category, action = super(SchemaGenerator, self).get_key(path, method, callback)

        if category == action:
            path, params = helpers.normalize_url(path)
            path = path.strip('/').split('/')
            if len(path) >= 2:
                action = path[-1]
                category = path[-2]

        return (category, action)


    def get_keys(self, subpath, method, view):
        """
        Return a list of keys that should be used to layout a link within
        the schema document.

        /users/                   ("users", "list"), ("users", "create")
        /users/{pk}/              ("users", "read"), ("users", "update"), ("users", "delete")
        /users/enabled/           ("users", "enabled")  # custom viewset list action
        /users/{pk}/star/         ("users", "star")     # custom viewset detail action
        /users/{pk}/groups/       ("users", "groups", "list"), ("users", "groups", "create")
        /users/{pk}/groups/{pk}/  ("users", "groups", "read"), ("users", "groups", "update"), ("users", "groups", "delete")
        """
        if hasattr(view, 'action'):
            # Viewsets have explicitly named actions.
            action = view.action
        else:
            # Views have no associated action, so we determine one from the method.
            if is_list_view(subpath, method, view):
                action = 'list'
            else:
                action = self.default_mapping[method.lower()]

        named_path_components = [
            component for component
            in subpath.strip('/').split('/')
            if '{' not in component
        ]

        if is_custom_action(action):
            # Custom action, eg "/users/{pk}/activate/", "/users/active/"
            return named_path_components[:-1] + [action]
            '''
            if len(view.action_map) > 1:
                action = self.default_mapping[method.lower()]
                if action in self.coerce_method_names:
                    action = self.coerce_method_names[action]
                return named_path_components + [action]
            else:
                return named_path_components[:-1] + [action]
            '''

        if action in self.coerce_method_names:
            action = self.coerce_method_names[action]

        # Default action, eg "/users/", "/users/{pk}/"
        return named_path_components + [action]
