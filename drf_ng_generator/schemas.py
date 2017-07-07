from rest_framework import schemas

from . import helpers







class SchemaGenerator(schemas.SchemaGenerator):
    known_actions = (
        'create', 'read', 'retrieve', 'list',
        'update', 'partial_update', 'destroy',
        'GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'
    )


    def get_link(self, path, method, callback):
        link = super(SchemaGenerator, self).get_link(path, method, callback)
        link._drf_view = callback.cls()
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
