import re
from . import helpers





class SchemaConverter:
    def __init__(self, schema=None):
        self.schema = schema


    def get_common_url(self, strList):
        "Given a list of strings, returns the longest common leading component"
        if not strList: return ''
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
            'alias':{}
        }

        for point_name,link in point.items():
            url, url_params = helpers.normalize_url(link.url)
            action = helpers.to_camelCase(point_name)

            point_api['commonUrlParams'] += url_params
            point_api['api'][action] = {
                'url': url,
                'method': link.action.upper(),
                'contentType': link.encoding
            }

            if point_name in ['destroy', 'delete'] and ':id/' in url:
                point_api['alias']['deleteById'] = point_name
                point_api['alias']['destroyById'] = point_name
            elif point_name in ['retrieve', 'get', 'read'] and ':id/' in url:
                point_api['alias']['findById'] = point_name
            elif 'list' in point_name.lower():
                point_api['api'][action]['options'] = {
                    'isArray': 'true'
                }
            elif point_name == 'partial_update':
                point_api['alias']['updateAttributes'] = 'partialUpdate'

        point_api['commonUrl'] = self.get_common_url([
            p['url']
            for k,p in point_api['api'].items()
        ])
        if 'id' in point_api['commonUrlParams']  and ':id/' not in point_api['commonUrl']:
            if point_api['commonUrl'][-1] == '/':
                point_api['commonUrl'] += ':id/'
            else:
                point_api['commonUrl'] += '/:id/'

        point_api['commonUrlParams'] = list(set(point_api['commonUrlParams']))
        return point_api



    def convert(self, schema=None):
        api_schema = {}
        schema = schema or self.schema
        for k,v in schema.data.items():
            api_schema[k] = self.api_point_to_definition(v)

        return api_schema
