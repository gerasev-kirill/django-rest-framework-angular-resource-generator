import re





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
