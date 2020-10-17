import re, json
from rest_framework.views import APIView

DRF_OLD_ACTION_MAP = {
    'read': 'retrieve',
    'delete': 'destroy'
}



def normalize_url(url):
    url = re.sub('\{pk\}', '{id}', url)
    url_params = re.findall(r"\{([A-Za-z0-9_]+)\}", url)
    url = re.sub('\{', ':', url)
    url = re.sub('\}', '', url)
    return url, url_params



def to_camelCase(text):
    text = re.sub(r'(?!^)_([a-zA-Z])', lambda m: m.group(0).upper(), text)
    text = text.replace('_','')
    return text


def view_to_str(o):
    # o.__module__ + "." + o.__class__.__qualname__ is an example in
    # this context of H.L. Mencken's "neat, plausible, and wrong."
    # Python makes no guarantees as to whether the __module__ special
    # attribute is defined, so we take a more circumspect approach.
    # Alas, the module name is explicitly excluded from __qualname__
    # in Python 3.

    module = o.__class__.__module__
    if module is None or module == str.__class__.__module__:
        return o.__class__.__name__  # Avoid reporting __builtin__
    else:
        return module + '.' + o.__class__.__name__




def resolve_api_callback_by_name(api_doc, viewset_name, action_name):
    doc = api_doc.get(viewset_name, None)
    if not doc:
        return None, None, None
    action_name = doc['alias'].get(action_name, action_name)
    action = doc['api'].get(action_name, None)
    if not action:
        # DEPRECATED for drf>=3.12
        for k in DRF_OLD_ACTION_MAP:
            if k in doc['api'] and action_name == DRF_OLD_ACTION_MAP[k]:
                action = doc['api'][k]
                break
    if not action:
        return None, None, None

    view = action['view'].__class__
    action_name = action['action']

    if not hasattr(view, action_name) and DRF_OLD_ACTION_MAP.get(action_name, None):
        if hasattr(view, DRF_OLD_ACTION_MAP[action_name]):
            action_name = DRF_OLD_ACTION_MAP[action_name]

    if not hasattr(view, action_name):
        actions = getattr(view, 'action_map', {}) or getattr(view, 'actions', {})
        for method, alias in actions.items():
            if action_name == alias:
                action_name = alias

    if not hasattr(view, action_name):
        return None, None, None

    data = {}
    data[action['method'].lower()] = action_name
    callback = view.as_view(data)

    return callback, action['url'], action['method'].lower()



class ViewEncoder(json.JSONEncoder):
     def default(self, obj):
         if isinstance(obj, APIView):
             return obj.__class__.__name__
         return super(ViewEncoder, self).default(obj)


def dumps_api_doc(api_doc):
    return json.dumps(
        api_doc,
        cls=ViewEncoder
    )
