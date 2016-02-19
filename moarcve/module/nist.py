import gzip
import lxml.html  # @UnresolvedImport
from moarcve.core import log
from moarcve.module._base import ModuleBase
from moarcve.net import get
from moarcve.util import get_cve_tuple
import moarcve.database as db
import os
from moarcve import data_path
import datetime


def isempty(txt):
    if txt is None or txt == '':
        return True
    return False


def clean(txt):
    if txt is None: return ''  # @IgnorePep8
    return txt.strip()


class Module(ModuleBase):

    def __init__(self, conf=None):
        super(Module, self).__init__('nist', fmt='nvd', conf=conf)
        self.reinit()

    def run(self):
        log.info('[%s/%s] parsing', self.name, self.fmt)
        url = self.conf.get('module.%s' % self.name, 'root')
        return self.parse(get(url))

    def reinit(self):
        self.tree = None

    def parse(self, response):
        self.reinit()
        if response.status_code != 200:
            log.error('Cannot get url: %s %s', response.status_code,
                      response.url)
            return False
        tree = lxml.html.fromstring(response.text)
        self.tree = tree
        for elm in tree.xpath('//a'):
            self.parse_element(elm)
        return True

    def parse_element(self, elm):
        href = elm.get('href')
        if isempty(href):
            return False
        if not href.endswith('.meta'):
            return False
        meta = self.parse_meta(elm)
        url = meta['href'].replace('meta', 'xml.gz')
        gz = get(url)
        txt = gzip.decompress(gz.content)  # @UndefinedVariable
        tree = lxml.html.fromstring(txt)
        for entry in tree.xpath('//entry'):
            try:
                self.parse_entry(entry)
            except Exception as e:
                log.error('Error: %s', e)

    def parse_meta(self, elm):
        response = get(elm.get('href'))
        meta = {
            'href': elm.get('href'),
            'text': elm.text
        }
        areint = ['size', 'zipSize', 'gzSize']
        for line in [clean(line) for line in response.text.split('\n')]:
            k, v = line.split(sep=':', maxsplit=1)
            if k in areint:
                v = int(v)
            meta[k] = v
        return meta

    def parse_entry(self, entry):
        with db.session.session_scope() as session:
            log.debug('=== entry ===',)
            cveid = entry.find('cve-id')
            if cveid is None:
                log.error('No cveid')
                return False
            t = get_cve_tuple(cveid.text)
            cve = session.query(db.Cve)\
                .filter(db.Cve.cve_id == t.cve_id)\
                .filter(db.Cve.year == t.year).first()
            if cve is not None:
                return False
            cve = db.Cve()
            for child in entry.iterchildren():
                if child.tag == 'cve-id':
                    t = get_cve_tuple(child.text)
                    setattr(cve, 'year', t[0])
                    setattr(cve, 'cve_id', t[1])
                else:
                    value = child.text
                    setattr(cve, child.tag.replace('-', '_'), value)
            session.add(cve)
            session.commit()


if __name__ == '__main__':
    import logging
    from moarcve.core import init_cache
    from moarcve.conf import Configuration
    conf = Configuration()
    init_cache(conf)
    logging.basicConfig()
    m = Module(conf=Configuration())
    m.run()
