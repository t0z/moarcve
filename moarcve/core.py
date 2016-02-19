import os
import logging
import requests_cache
import importlib
import moarcve
from moarcve.database import Run
from moarcve.conf import Configuration
from moarcve.database import session_scope

log = logging.getLogger('moarcve')
log.setLevel(logging.DEBUG)


class Meta(object):

    def __init__(self):
        self.lastModifiedDate = None
        self.size = None
        self.zipSize = None
        self.gzSize = None
        self.sha256 = None


def init_cache(conf):
    requests_cache.install_cache(conf.get('cache', 'requests_cache'))


class RunStatus(object):
    done = 'done'
    error = 'error'
    pending = 'pending'


class Core(object):

    def __init__(self, urls=None, onlySSL=True, modules=['nist']):
        self.onlySSL = onlySSL
        self.urls = urls
        self.conf = Configuration()
        self._init_directories()
        init_cache(self.conf)
        self.modules_name = modules

    def _init_directories(self):
        paths = []
        [os.mkdir(path) if not os.path.exists(path) else None
            for path in paths]

    def run_package(self, name):
        log.debug('==== %s ====', name)
        from time import time
        started_on = time()
        package = importlib.import_module(name)
        module = package.Module(conf=self.conf)
        module.run()
        elapsed = time() - started_on
        log.debug('end %s in %ss', name, elapsed)

    def run(self):
        runid = None
        status = RunStatus.pending
        error = None
        with session_scope() as session:
            run = Run()
            from datetime import datetime
            run.started_on = datetime.now()
            run.stopped_on = None
            run.status = 'pending'
            session.add(run)
            session.commit()
            runid = run.id
        log.debug('Runid: %s', runid)
        log.debug('=== %s (%s) ===', moarcve.__progname__, moarcve.__version__)
        for name in ['moarcve.module.%s' % name for name in self.modules_name]:
            try:
                self.run_package(name)
                status = RunStatus.done
            except Exception as e:
                log.error('Exception in package %s\n%s', name, e)
                status = RunStatus.error
                error = str(e)
        with session_scope() as session:
            log.info('runid: %s', runid)
            run = session.query(Run).filter(Run.id==runid).first()
            run.stopped_on = datetime.now()
            run.status = status
            run.error = error
            session.add(run)
            session.commit()

    def get(self, cve):
        tokens = cve.split('-')
        return tokens

if __name__ == '__main__':
    from moarcve.database import session
    conf = Configuration()
    session.init(conf)
    logging.basicConfig()
    core = Core()
    core.run()
