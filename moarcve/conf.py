import os
from configparser import ConfigParser
import moarcve


def replace():
    return {
        'data_path': moarcve.data_path,
        'base_path': moarcve.base_path
    }


class Configuration(ConfigParser):

    def __init__(self,
                 paths=[os.path.join(moarcve.data_path, 'moarcve.conf')],
                 *a, **ka):
        self.paths = paths
        super(Configuration, self).__init__(*a, **ka)
        self.read(self.paths)

    def get(self, section, option, *a, **ka):
        if 'vars' in ka and ka['vars'] is not None:
            print('vars: %s' % ka['vars'])
            ka['vars'].update(replace())
        else:
            ka['vars'] = replace()
        return super(Configuration, self).get(section, option, *a, **ka)

if __name__ == '__main__':
    conf = Configuration()
    print('url/root %s' % conf.get('url', 'root'))
    print('cache/path %s' % conf.get('cache', 'path'))
