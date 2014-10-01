# -*- coding: utf-8 -*-
import os
import sys

try:
    # python 3
    from urllib import request
except:
    # python 2
    import urllib as request

from setuptools import setup, find_packages
from setuptools.command import easy_install
from setuptools.command.test import test as TestCommand

from linkmanager import (
    __appname__, __version__,
    __website__,
    __licence__, __author__
)

base = os.path.dirname(__file__)

readme = open(os.path.join(base, 'README.rst')).readlines()
readme = "".join(readme[:12] + readme[34:])
changelog = open(os.path.join(base, 'HISTORY.rst')).read()

# use this option (on end) when using on debian rules : createdeb
print(sys.argv[-1])
if sys.argv[-1] == 'createdeb':
    sys.argv.pop()
else:
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

man_path = '/usr/share/man/man1/'


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = [
            '-vv', 'linkmanager/tests/tests.py',
            '--cov=linkmanager',
            '--cov-report', 'term-missing'
        ]
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)
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
    include_package_data=True,
    scripts=['linkm'],
    data_files=[
        ('/etc/', ['linkmanager.conf']),
        (man_path, ['docs/linkmanager.1.gz']),
        # symlink : man linkm == man linkmanager
        (man_path, ['docs/linkm.1.gz']),
        ('/usr/bin/', ['linkmanager.zsh'])
    ],
    install_requires=required,
    tests_require=['pytest'],
    cmdclass={'test': PyTest},
    zip_safe=True
)
if sys.argv != ['-c', 'egg_info', '--egg-base', 'pip-egg-info']:
    exit(0)

bashrc = '/etc/bash.bashrc'
zshrc = '/etc/zsh/zshrc'
bash_cmd = 'eval "$(register-python-argcomplete linkm)"\n'
zsh_cmd = "source linkmanager.zsh\n"
if os.path.isfile(bashrc):
    with open(bashrc, 'r+') as f:
        readlines = f.readlines()
        if bash_cmd not in readlines:
            f.write(bash_cmd)

if os.path.isfile(zshrc):
    with open(zshrc, 'r+') as f:
        readlines = f.readlines()
        if zsh_cmd not in readlines:
            f.write(zsh_cmd)

# os.popen('$SHELL')
