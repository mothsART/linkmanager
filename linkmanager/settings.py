DEBUG = True

### Database
TEST = False
DB = {
    'ENGINE': 'redis',
    'HOST': 'localhost',
    'PORT': 6379,
    # By convention, bases 0-14 are used to production and after to test
    'DB_NB': 0,
    'TEST_DB_NB': 15
}

### Cache
ACTIVE_CACHE = True
CACHE_PATH = "/var/linkmanager/cache"
CACHE_MAX_SIZE = "1G"

### Minimizer
# * http://tinyurl.com/
#   MINIMIZER = "http://tinyurl.com/api-create.php?url="
# * https://bitly.com/

MINIMIZE_URL = True
MINIMIZER = "http://www.urlmin.com/api?url="
MINIMIZER_MIN_SIZE = 20

### Search
# 1 <= NB_AUTOSUGGESTIONS <= 40
NB_AUTOSUGGESTIONS = 10
NB_RESULTS = 50

### CLI : specific to shell usage
INDENT = 4

### WEBSERVICE
HTTP_PORT = 7777
BROWSER = 'firefox'

# nb of Workers
WORKERS = 5
