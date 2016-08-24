import re



class SchemaConverter:
    def __init__(self, schema=None):
        self.schema = schema

    def toCamelCase(self, text):
        text = re.sub(r'(?!^)_([a-zA-Z])', lambda m: m.group(0).upper(), text)
        text = text.replace('_','')
        return text

    def findCommonPrefix(self, strList):
        "Given a list of strings, returns the longest common leading component"
        if not strList: return ''
        s1 = min(strList)
        s2 = max(strList)
        for i, c in enumerate(s1):
            if c != s2[i]:
                return s1[:i]
        return s1

    def djangoUrlToAngular(self, url):
        url = url.replace('{', ':').replace('}', '')
        if url[-1]=='/':
            url += ' '
        return url

    def apiPointToDict(self, point):
        has_id_in_url = False
        data = {}
        alias = {}
        urls = []
        for k,v in point.items():
            urls.append(v.url)
        commonUrl = self.findCommonPrefix(urls)

        for k,v in point.items():
            url = self.djangoUrlToAngular(v.url)
            if url.find(':id/')>-1:
                has_id_in_url = True
            action = self.toCamelCase(k)
            data[action] = {
                'url': url,
                'method': v.action.upper(),
                'contentType': v.encoding
            }
            if k == 'destroy' and url.find(':id/')>-1:
                alias['deleteById'] = 'destroy'
                alias['destroyById'] = 'destroy'
            if k in ['retrieve', 'get'] and url.find(':id/')>-1:
                alias['findById'] = k
            if k.find('list')>-1:
                data[action]['options']={
                    'isArray': 'true'
                }


        if has_id_in_url and '{pk}/' not in commonUrl:
            if commonUrl[-1] == '/':
                commonUrl += '{pk}/'
            else:
                commonUrl += '/{pk}/'
        return {
            'commonUrl': self.djangoUrlToAngular(commonUrl),
            'api': data,
            'alias': alias,
            'hasIdInUrl': has_id_in_url
        }


    def convert(self, schema=None):
        apiDict = {}
        if not schema:
            schema = self.schema

        for k,v in schema.data.items():
            apiDict[k] = self.apiPointToDict(v)
        return apiDict
