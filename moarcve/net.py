import requests
from urllib import parse
from moarcve.core import log

class BadRequest(Exception):
    def __init__(self, code, error):
        super(BadRequest, self).__init__('%s %s' % (code, error))

def get(url, ssl=False, checkStatus=True):
    compo = parse.urlparse(url)._asdict()
    if ssl:
        if not compo['scheme'].endswith('s'):
            compo['scheme'] += 's'
    url = parse.urlunparse(compo.values())
    log.debug('HTTP/GET %s', url)
    response = requests.get(url)
    if checkStatus is True:
        if response.status_code != 200:
            raise BadRequest(response.status_code,
                      response.error)
    return response