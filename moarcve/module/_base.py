class ModuleBase(object):

    class error(object):
        class MissingFormat(Exception): pass

    def __init__(self, name, fmt='nvd', conf=None):
        self.name = name
        self.fmt = fmt
        self.conf = conf

    def run(self, *a, **k):
        raise NotImplementedError()