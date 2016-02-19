#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import moarcve  # @UnresolvedImport

sys.path.append('.')

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


# if sys.argv[-1] == 'publish':
#    os.system('python setup.py sdist upload')
#    sys.exit()

requires = []
with open(os.path.join(os.path.dirname(__file__), 'requirements.txt')) as f:
    requires = f.read().strip().split('\n')
print('req: %s' % requires)
with open(os.path.join(os.path.dirname(__file__), 'README.md')) as f:
    readme = f.read()

packages = [
    'moarcve',
]

package_data = {
    'data': 'moarcve/data'
}

scripts = ['moarcve/script/moarcve']

classifiers = [
]


setup(
    name='moarcve',
    version=moarcve.__version__,
    description='',
    long_description=readme,
    packages=packages,
    package_data=package_data,
    install_requires=requires,
    author=moarcve.__author__,
    author_email=moarcve.__email__,
    url='',
    license='MIT',
    classifiers=classifiers,
    scripts=scripts,
)
