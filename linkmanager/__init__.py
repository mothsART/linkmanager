# python2 "raw_input()" was renamed to input() on python3
try:
    input = raw_input
except NameError:
    pass

import redis

from .settings import NB_RESULTS
from .translation import gettext as _
from linkmanager import validators

r = redis.StrictRedis(host='localhost', port=6379, db=0)
indentation = 4


def color(c_str, color='\033[1;42m'):
    return '{color}{c_str}{cb}'.format(color=color, c_str=c_str, cb='\033[1;m')


def properties_input(l):
    print(color('%s properties :' % l))
    tags = input(
        ' ' * indentation
        + color(_('tags (separate with ",")'), color='\033[0;32m')
        + ' : '
    ).split(',')
    priority = input(
        ' ' * indentation
        + color(
            _('priority value (integer value between 1 and 10)'),
            color='\033[0;32m'
        )
        + ' : '
    )
    while True:
        try:
            if priority == '':
                priority = 1
            int(priority)
            break
        except:
            priority = input(
                ' ' * indentation
                + color(
                    _('priority value value not range between 1 and 10, retry'),
                    color='\033[0;32m'
                )
                + ' : '
            )
    description = input(
        ' ' * indentation
        + color(
            _('give a description'),
            color='\033[0;32m'
        )
        + ' : '
    )
    return tags, priority, description


def addlink(links=None):
    if not links:
        links = input(
            _('Give one or several links (separate with space)') + ': '
        )
        links = links.split()
    # keep only URLs that validate
    links = [l for l in links if validators.URLValidator()(l)]
    for l in links:
        #properties_input(l)

        tags = ['shell', 'linux']
        priority = 1
        description = ''
        for tag in tags:
            r.sadd(tag, l)
        r.zadd('links_priority', priority, l)
        #import uuid
        #str(uuid.uuid1())
        #p = [priority, description] + tags
        #r.rpush(l, *p)
    #print 'add', links


def updatelink(links=None):
    print('update')


def deletelink(link=None):
    print('delete')


def searchlink(tags=None):
    print(r.zrangebyscore('links_priority', 0, NB_RESULTS, withscores=True))
    #print(r.zrank('links_priority', 'http://super.fr'))
    # No tags : give all values
    if not tags:
        for key in r.keys():
            print(key, r.type(key))
            #print(key, r.type(key), r.smembers(key))
        return
    # One tag : give all associate links
    if len(tags) == 1:
        print(r.smembers(tags[0]))
    # Multi tags : give common links
    else:
        print(r.sinter(tags))
