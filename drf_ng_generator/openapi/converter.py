from collections import OrderedDict
from .. import helpers


class SchemaConverter:

    def __init__(self, schema=None):
        self.schema = schema

    def get_common_url(self, strList):
        "Given a list of strings, returns the longest common leading component"
        if not strList:
            return ''
        s1 = min(strList)
        s2 = max(strList)
        for i, c in enumerate(s1):
            if c != s2[i]:
                return s1[:i]
        return s1

    def api_point_to_definition(self, resource_name, all_points):
        point_api = {
            'commonUrl': '',
            'commonUrlParams': [],
            'api': {},
            'alias': {}
        }

        for point in all_points:
            url, url_params = helpers.normalize_url(point['path'])
            action = helpers.to_camelCase(point['description']['x-django']['function'])
            content_type = ''
            if 'application/json' in point.get('requestBody', {}).get('content', {}):
                content_type = 'application/json'
            point_api['commonUrlParams'] += url_params

            point_api['api'][action] = {
                'actionName': action,
                'url': url,
                'method': point['method'].upper(),
                'contentType': content_type,
                'view': point['description']['x-django']['view'],
                #'view': point['description']['x-django']['view'].split('.')[-1],
                'action': point['description']['x-django']['function'],
                'options': OrderedDict()
            }
            if point['method'].upper() in ['GET']:
                point_api['api'][action]['options']['cancellable'] = 'true'

            if point['description']['x-django']['function'] in ['destroy', 'delete'] and ':id/' in url:
                point_api['alias']['deleteById'] = action
                point_api['alias']['destroyById'] = action
            elif point['description']['x-django']['function'] in ['retrieve', 'get', 'read'] and ':id/' in url:
                point_api['alias']['findById'] = action
            elif 'list' in point['description']['x-django']['function'].lower():
                point_api['api'][action]['options']['isArray'] = 'true'
            elif point['description']['x-django']['function'] == 'partial_update':
                point_api['alias']['updateAttributes'] = 'partialUpdate'
            if point['description']['x-django']['function'] == 'list':
                point_api['alias']['find'] = 'list'
                point_api['alias']['query'] = 'list'


        point_api['commonUrl'] = self.get_common_url([
            p['url']
            for k, p in point_api['api'].items()
        ])
        if 'id' in point_api['commonUrlParams'] and ':id/' not in point_api['commonUrl']:
            if point_api['commonUrl'][-1] == '/':
                point_api['commonUrl'] += ':id/'
            else:
                point_api['commonUrl'] += '/:id/'

        point_api['commonUrlParams'] = list(set(point_api['commonUrlParams']))
        point_api['commonUrlParams'].sort()
        # remove overrides from alias
        for alias_name, name in point_api['alias'].items():
            if alias_name in point_api['api']:
                del point_api['alias'][alias_name]

        return point_api


    def sort_api(self, api_schema):
        sorted_api_schema = OrderedDict()
        for point_name in sorted(api_schema.keys()):
            point_api = api_schema[point_name]
            point_api['api'] = [
                point_api['api'][name]
                for name in sorted(point_api['api'].keys())
            ]
            point_api['alias'] = [
                {'alias': name, 'actionName': point_api['alias'][name]}
                for name in sorted(point_api['alias'].keys())
            ]
            sorted_api_schema[point_name] = point_api
        return sorted_api_schema

    def convert(self, schema=None, order=False, ignore_viewset_names=False):
        api_schema = {}
        schema = schema or self.schema
        schema_by_view = {}
        for pathname, data in schema['paths'].items():
            for http_method, http_description in data.items():
                view_name = helpers.view_to_str(http_description['x-django']['view'])
                schema_by_view[view_name] = schema_by_view.get(view_name, [])
                schema_by_view[view_name].append({
                    'path': pathname,
                    'method': http_method,
                    'description': http_description
                })

        for k, v in schema_by_view.items():
            resource_name = k.split('.')[-1].split('Viewset')[0].split('View')[0]
            resource_definition = self.api_point_to_definition(resource_name, v)
            if ignore_viewset_names:
                resource_name = resource_definition['commonUrl'].strip('/').replace(':id', '').strip('/').split('/')[-1]
            api_schema[resource_name] = resource_definition


        common_urls = []
        for n in api_schema:
            params = api_schema[n]
            common_urls.append(params['commonUrl'])
        api_url_base = self.get_common_url(common_urls)
        if api_url_base == '/':
            api_url_base = ''
        if api_url_base and api_url_base[-1] == '/':
            api_url_base = api_url_base[:-1]

        for n in api_schema:
            api_schema[n]['commonUrl'] = api_schema[n]['commonUrl'].replace(
                api_url_base,
                '',
                1
            )
            for p in api_schema[n]['api']:
                api_schema[n]['api'][p]['url'] = api_schema[n]['api'][p]['url'].replace(
                    api_url_base,
                    '',
                    1
                )
        if order:
            api_schema = self.sort_api(api_schema)
        return api_schema, api_url_base
