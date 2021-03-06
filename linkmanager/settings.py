import os
import configparser
import logging

logger = logging.getLogger()

from clint.textui.colored import white

from linkmanager.translation import gettext as _

DEBUG = True
SERVER = False

# -- Database
DB = {
    'ENGINE': 'redis',
    'HOST': 'localhost',
    'PORT': 6379,
    'DB_NB': 0
}

# -- Cache
ACTIVE_CACHE = True
CACHE_PATH = "/var/linkmanager/cache"
CACHE_MAX_SIZE = "1G"

# -- Minimizer
# * http://tinyurl.com/
#   MINIMIZER = "http://tinyurl.com/api-create.php?url="
# * https://bitly.com/

MINIMIZE_URL = True
MINIMIZER = "http://www.urlmin.com/api?url="
MINIMIZER_MIN_SIZE = 25

# -- Search
# 1 <= NB_AUTOSUGGESTIONS <= 40
NB_AUTOSUGGESTIONS = 10
NB_RESULTS = 50

# -- CLI : specific to shell usage
INDENT = 4

# nb of Workers
WORKERS = 5

# -- WEBSERVICE
HTTP_HOST = '127.0.0.1'
HTTP_PORT = 7777
BROWSER = 'firefox'
READ_ONLY = False
EDITMODE = False
DELETEDIALOG = True
UPDATE = True
DELETE = True

def get(func, section, **kwargs):
    global path
    value = list(kwargs.values())[0]
    try:
        return getattr(config, func)(section, list(kwargs.keys())[0])
    except configparser.NoOptionError:
        return value
    except:
        logger.warning(white(_(
            'WARNING! {path} : bad value on "{name}" (Default: {value})'
        ).format(
            path=path,
            name=list(kwargs.keys())[0],
            value=value
        ), bold=True, bg_color='yellow'))
        return value


def update_conf():
    global DEBUG
    DEBUG = get('getboolean', 'DEFAULT', DEBUG=DEBUG)
    global SERVER
    SERVER = get('getboolean', 'DEFAULT', SERVER=SERVER)
    global WORKERS
    WORKERS = get('getint', 'DEFAULT', WORKERS=WORKERS)

    global DB
    DB['ENGINE'] = get('get', 'DB', ENGINE=DB['ENGINE'])
    DB['HOST'] = get('get', 'DB', HOST=DB['HOST'])
    DB['PORT'] = get('getint', 'DB', PORT=DB['PORT'])
    DB['DB_NB'] = get('getint', 'DB', DB_NB=DB['DB_NB'])

    global ACTIVE_CACHE
    ACTIVE_CACHE = get('getboolean', 'CACHE', ACTIVE_CACHE=ACTIVE_CACHE)
    global CACHE_PATH
    CACHE_PATH = get('get', 'CACHE', CACHE_PATH=CACHE_PATH)
    global CACHE_MAX_SIZE
    CACHE_MAX_SIZE = get('get', 'CACHE', CACHE_MAX_SIZE=CACHE_MAX_SIZE)

    global MINIMIZE_URL
    MINIMIZE_URL = get('getboolean', 'MINIMIZER', MINIMIZE_URL=MINIMIZE_URL)
    global MINIMIZER
    MINIMIZER = get('get', 'MINIMIZER', MINIMIZER=MINIMIZER)
    global MINIMIZER_MIN_SIZE
    MINIMIZER_MIN_SIZE = get(
        'getint', 'MINIMIZER',
        MINIMIZER_MIN_SIZE=MINIMIZER_MIN_SIZE
    )

    global NB_AUTOSUGGESTIONS
    NB_AUTOSUGGESTIONS = get(
        'getint', 'SEARCH',
        NB_AUTOSUGGESTIONS=NB_AUTOSUGGESTIONS
    )
    global NB_RESULTS
    NB_RESULTS = get('getint', 'SEARCH', NB_RESULTS=NB_RESULTS)
    global INDENT
    INDENT = get('getint', 'CLI', INDENT=INDENT)

    global HTTP_HOST
    HTTP_HOST = get('get', 'WEBAPP', HTTP_HOST=HTTP_HOST)
    global HTTP_PORT
    HTTP_PORT = get('getint', 'WEBAPP', HTTP_PORT=HTTP_PORT)
    global BROWSER
    BROWSER = get('get', 'WEBAPP', BROWSER=BROWSER)
    global READ_ONLY
    READ_ONLY = get('getboolean', 'WEBAPP', READ_ONLY=READ_ONLY)
    global UPDATE
    UPDATE = get('getboolean', 'WEBAPP', UPDATE=UPDATE)
    global DELETEDIALOG
    DELETEDIALOG = get('getboolean', 'WEBAPP', DELETEDIALOG=DELETEDIALOG)
    global DELETE
    DELETE = get('getboolean', 'WEBAPP', DELETE=DELETE)
    global EDITMODE
    EDITMODE = get('getboolean', 'WEBAPP', EDITMODE=EDITMODE)

config = configparser.ConfigParser()
# /etc config file
path = '/etc/linkmanager.conf'
if os.path.exists(path):
    c = config.read(path)
    update_conf()
# user config file
directory = os.path.join(
    os.path.expanduser("~"),
    '.config'
)
path = os.path.join(directory, 'linkmanager.conf')

if not os.path.exists(directory):
    os.makedirs(directory)

if not os.path.exists(path):
    with open(path, 'w') as f:
        f.write(open(os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'default.conf'
        ), 'r').read())
else:
    c = config.read(path)
    update_conf()


def set_user_conf(**kwargs):
    path = os.path.join(directory, 'linkmanager.conf')

    if not os.path.exists(directory):
        os.makedirs(directory)

    if not os.path.exists(path):
        with open(path, 'w') as f:
            f.write(open(os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                'default.conf'
            ), 'r').read())
    config = configparser.ConfigParser(comment_prefixes=(), allow_no_value=True)
    config.read(path)

    for section in kwargs:
        option = kwargs[section]
        # Create section if inexistant
        if not config.has_section(section):
            config.add_section(section)
        config.set(section, str(option[0]), str(option[1]))

    with open(path, 'w') as f:
        config.write(f)
