DEBUG = True

AUTHOR = 'Author name'
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
MINIMIZER = "https://www.googleapis.com/urlshortener/v1/url"
MINIMIZER_MIN_SIZE = 25

# -- Search
# 1 <= NB_AUTOSUGGESTIONS <= 40
NB_AUTOSUGGESTIONS = 10
NB_RESULTS = 50

# -- CLI : specific to shell usage
INDENT = 4

# nb of Workers
WORKERS = 5

# -- WEBAPP
HTTP_PORT = 7777
BROWSER = 'firefox'
READ_ONLY = False
UPDATE = True
DELETE = True
