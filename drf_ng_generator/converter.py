import coreapi
from collections import OrderedDict
from . import helpers


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

    def api_point_to_definition(self, point):
        point_api = {
            'commonUrl': '',
            'commonUrlParams': [],
            'api': {},
            'alias': {}
        }

        def add_point(point_name, link):
            url, url_params = helpers.normalize_url(link.url)
            action = helpers.to_camelCase(point_name)

            point_api['commonUrlParams'] += url_params
            point_api['api'][action] = {
                'actionName': action,
                'url': url,
                'method': link.action.upper(),
                'contentType': link.encoding,
                'view': link._view,
                'action': point_name,
                'options': OrderedDict()
            }
            if link.action.upper() in ['GET']:
                point_api['api'][action]['options']['cancellable'] = 'true'

            if point_name in ['destroy', 'delete'] and ':id/' in url:
                point_api['alias']['deleteById'] = point_name
                point_api['alias']['destroyById'] = point_name
            elif point_name in ['retrieve', 'get', 'read'] and ':id/' in url:
                point_api['alias']['findById'] = point_name
            elif 'list' in point_name.lower():
                point_api['api'][action]['options']['isArray'] = 'true'
            elif point_name == 'partial_update':
                point_api['alias']['updateAttributes'] = 'partialUpdate'
            if point_name == 'list':
                point_api['alias']['find'] = 'list'
                point_api['alias']['query'] = 'list'

        for point_name, link in point.items():
            if isinstance(link, coreapi.document.Object):
                for _point_name, _link in link.items():
                    if isinstance(_link, coreapi.document.Object):
                        for _point_name, __link in _link.items():
                            add_point(_point_name, __link)
                    else:
                        add_point(_point_name, _link)
            else:
                add_point(point_name, link)

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

    def convert(self, schema=None, order=False):
        api_schema = {}
        schema = schema or self.schema
        for k, v in schema.data.items():
            api_schema[k] = self.api_point_to_definition(v)

        common_urls = []
        for n in api_schema:
            params = api_schema[n]
            common_urls.append(params['commonUrl'])
        api_url_base = self.get_common_url(common_urls)
        if api_url_base == '/':
            api_url_base = ''
        if api_url_base[-1] == '/':
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
