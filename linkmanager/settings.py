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

### Search
NB_RESULTS = 10
INDENT = 4
