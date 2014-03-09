# encoding=utf8

import sys
from setuptools import setup, find_packages
from linkmanager import __version__
import os

base = os.path.dirname(__file__)

readme = open(os.path.join(base, 'README.rst')).readlines()
readme = "".join(readme[19:])
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
        dlinks.append(url[4:])
        url = url[:url.find('@')]
        required.append(url[url.rfind('/') + 1:])

setup(
    name='linkmanager',
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
    author='Jérémie Ferry',
    author_email='jerem.ferry@gmail.com',
    url='https://github.com/mothsART/linkmanager',
    license='BSD',
    packages=find_packages(exclude=['tests']),
    #include_package_data=True,
    #zip_safe=True,
    scripts=['linkm.py'],
    dependency_links=dlinks,
    install_requires=required
)
