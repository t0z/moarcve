
from flask import Flask
from flask_restful import Api
from moarcve.srv import resource
from moarcve.core import log


class Application(object):

    def __init__(self, conf=None):
        log.info('[%s] Init', self.__class__.__name__)
        self.conf = conf
        self.app = Flask(__name__)
        self.api = Api(self.app)
        self.debug = True
        self.init_configure()
        self.init_api()

    def init_configure(self):
        log.info('[%s] Init configure', self.__class__.__name__)
        self.app.config['SECRET_KEY'] = self.conf.get('httpd', 'secret')
        self.app.config['BUNDLE_ERRORS'] = True

    def init_api(self):
        log.info('[%s] Init api', self.__class__.__name__)
        resource.Static.static_path = self.conf.get('ui', 'html')
        self.api.add_resource(resource.Static, '/ui', '/ui/<path:path>', endpoint="ui")

        self.api.add_resource(resource.Cve,
                              '/api/cve',
                              '/api/cve/<year>',
                              '/api/cve/<year>/<cve_id>',
                              endpoint='api/cve',)

    def run(self, *a, **ka):
        return self.app.run(debug=self.debug,
                            host=self.conf.get('httpd', 'host'),
                            port=self.conf.getint('httpd', 'port'))


def main(conf=None, *a, **ka):
    app = Application(conf=conf)
    app.run(*a, **ka)

if __name__ == '__main__':
    import moarcve.database as database
    from moarcve.conf import Configuration
    conf = Configuration()
    database.session.init(conf)
    app = Application(conf=conf)
    app.run(debug=True)
