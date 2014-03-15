# encoding=utf8

import sys

try:
    # python 3
    from urllib import request
except:
    # python 2
    import urllib as request

from setuptools import setup, find_packages
from setuptools.command import easy_install

from linkmanager import (
    __appname__, __version__,
    __website__,
    __licence__, __author__
)
import os

base = os.path.dirname(__file__)

readme = open(os.path.join(base, 'README.rst')).readlines()
readme = "".join(readme[23:])
changelog = open(os.path.join(base, 'HISTORY.rst')).read()
#todo = open(os.path.join(base, 'TODO.rst')).read()

clint_archive = request.urlopen(
    "http://github.com/mothsART/clint/archive/master.zip"
)
output = open('clint.zip', 'wb')
output.write(clint_archive.read())
output.close()
easy_install.main(['-U', 'clint.zip'])

required = []
dlinks = []

r_file = 'python2_requirements.txt'
if sys.version_info[0] == 3:
    r_file = 'python3_requirements.txt'
    if sys.version_info[1] >= 3:
        r_file = 'base.txt'

with open(
    os.path.join(base, 'requirements', r_file)
) as f:
    required = f.read().splitlines()

for line in required:
    if line.startswith('-r '):
        required.remove(line)
        with open(os.path.join(base, 'requirements', line[3:])) as f:
            required += f.read().splitlines()
    elif line.startswith('-e '):
        required.remove(line)

a = __author__
author = a[:a.find("<") - 1]
author_email = a[a.find("<") + 1:-1]

setup(
    name=__appname__,
    version=__version__,
    description='Manage your link on terminal',
    long_description=readme + '\n' + changelog
    + '\n\n.. _pip: http://www.pip-installer.org/',  # + '\n' + todo
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.3',
        'Topic :: Terminals :: Terminal Emulators/X Terminals',
    ],
    keywords='manager link links URL prompt shell',
    platforms=["Linux"],
    author=author,
    author_email=author_email,
    url=__website__,
    license=__licence__,
    packages=find_packages(exclude=['tests']),
    scripts=['linkm'],
    data_files=[('share/man/man1/', ['linkmanager/man/linkmanager.1'])],
    install_requires=required,
    zip_safe=True
)
