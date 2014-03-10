# encoding=utf8

import sys
from setuptools import setup, find_packages
from linkmanager import (
    __appname__, __version__,
    __website__,
    __licence__, __author__
)
import os

base = os.path.dirname(__file__)

readme = open(os.path.join(base, 'README.rst')).readlines()
readme = "".join(readme[22:])
changelog = open(os.path.join(base, 'HISTORY.rst')).read()
#todo = open(os.path.join(base, 'TODO.rst')).read()

required = []
dlinks = []

r_file = 'python2_requirements.txt'
if sys.version_info[0] == 3:
    r_file = 'python3_requirements.txt'

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
        url = line[3:]
        required.remove(line)
        dlinks.append(url)
        url = url[:url.find('@')]
        required.append(url[url.rfind('/') + 1:])

a = __author__
author = a[:a.find("<") - 1]
author_email = a[a.find("<") + 1:-1]

setup(
    name=__appname__,
    version=__version__,
    description='Manage your link on terminal',
    long_description=readme + '\n' + changelog,  # + '\n' + todo
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
    dependency_links=dlinks,
    install_requires=required,
    zip_safe=True
)
