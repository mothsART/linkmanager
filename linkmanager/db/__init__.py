import redis
import json
import uuid

from collections import OrderedDict

import datetime
from requests_futures.sessions import FuturesSession
from bs4 import BeautifulSoup

from linkmanager import settings


class MixinDb(object):
    """ Abstract DataBase Class """
    host = settings.DB['HOST']
    port = settings.DB['PORT']
    db_nb = settings.DB['DB_NB']
    properties = False

    def load(self, fixture):
        """ Load a string : json format """
        fixture = json.loads(fixture)
        # start_time = datetime.datetime.now()
        # session = FuturesSession(max_workers=settings.WORKERS)

        # urls = []
        # for link in fixture:
        #     if 'title' in fixture[link]:
        #         if fixture[link]['title'] == '':
        #             url = session.get(link)
        #         else:
        #             url = link
        #     else:
        #         url = session.get(link)
        #     urls.append((url, link))
        # for url in urls:
        #     title = ''
        #     if type(url) == str:
        #         continue
        #     try:
        #         result = url[0].result()
        #     except:
        #         # 404 page
        #         continue
        #     title = BeautifulSoup(result.content).title.string.strip()
        #     fixture.get(url[1])['title'] = title

        # elsapsed_time = datetime.datetime.now() - start_time
        # print("Elapsed time: %ss" % elsapsed_time.total_seconds())
        return self._add_links(fixture)


class RedisDb(MixinDb):
    """ Redis DataBase """

    def __init__(self, test=False):
        """ Create a Redis DataBase """
        if test:
            self.db_nb = settings.DB['TEST_DB_NB']
        self._db = redis.StrictRedis(
            host=self.host,
            port=self.port,
            db=self.db_nb
        )

    def _add_links(self, fixture):
        " Add links on Database"

        for link in fixture:
            value = fixture[link]

            if self._db.hexists('links_uuid', link):
                l_uuid = self._db.hget('links_uuid', link)
                # give a list of tags to removed on updating :
                # calculate difference between existing tags and new tags
                tags = set(self.tags(l_uuid)) - set(value['tags'])
                for tag in tags:
                    if self._db.scard(tag) == 1:
                        # Delete Tag if this link is the only reference
                        self._db.delete(tag)
                    else:
                        # Delete link refered by tag
                        self._db.srem(tag, l_uuid)
            else:
                l_uuid = str(uuid.uuid4())
                self._db.hset('links_uuid', link, l_uuid)

            for tag in value['tags']:
                for inc in range(len(tag)):
                    self._db.zadd(':compl', 0, tag[:inc])
                self._db.zadd(':compl', 0, tag + '*')
                self._db.sadd(tag, l_uuid)

            title = ''
            if 'title' in value:
                title = value['title']

            self._db.hmset(
                l_uuid,
                {
                    'title': title,
                    'name': link,
                    'real link': link,
                    'priority': value['priority'],
                    'description': value['description'],
                    'init date': value['init date'],
                    'update date': value['update date']
                }
            )
        return True

    def get_link_properties(self, link):
        " Return all properties correspond to a link"
        properties = {}
        l_uuid = self._db.hget('links_uuid', link)
        properties['tags'] = self.tags(l_uuid)
        p = self._db.hgetall(l_uuid)
        properties['real link'] = p[b"real link"].decode()
        properties['title'] = p[b"title"].decode()
        properties['priority'] = p[b"priority"].decode()
        properties['description'] = p[b"description"].decode()
        properties['init_date'] = p[b"init date"].decode()
        properties['update_date'] = p[b"update date"].decode()
        properties['l_uuid'] = l_uuid.decode()
        return properties

    def complete_tags(self, value=''):
        " Give a list of possible tags"
        # This is not random, try to get replies < MTU size
        rangelen = 50
        rank = self._db.zrank(':compl', value)
        # No tag to complete
        if not rank:
            return []
        compl = self._db.zrange(':compl', rank, rank + rangelen - 1)
        ###TODO : perform scalability
        # 2 algos for little and big database
        # alphabet = 'abcdefghijklmnopqrstuvwxyz'
        # b_value = ''
        # a_value = ''
        # last_c = ''
        # for v in value:
        #     pos = alphabet.find(v)
        #     a_value = b_value + alphabet[pos + 1]
        #     b_value = b_value[:-1] + last_c + alphabet[pos + 1]
        #     last_c = v
        #     print(self._db.zrank(':compl', a_value))
        complete_tags = []
        for c in compl:
            c = c.decode()
            if (
                not c.startswith(value)
                and len(complete_tags) >= settings.NB_AUTOSUGGESTIONS
            ):
                break
            if c.startswith(value) and c.endswith('*'):
                complete_tags.append(c[:-1])
        return complete_tags

    def tags(self, l_uuid=None):
        tags = []
        for key in self._db.keys():
            if self._db.type(key) == b'set':
                if not l_uuid:
                    tags.append(key.decode())
                    continue
                if self._db.sismember(key, l_uuid):
                    tags.append(key.decode())
        return sorted(tags)

    def link_exist(self, link):
        " Test if a link exist"
        if not self._db.hexists('links_uuid', link):
            return False
        return True

    def add_link(self, fixture):
        " Add one link on Database"
        fixture = json.loads(fixture)
        return self._add_links(fixture)

    def update_link(self, fixture):
        " Update one link on Database"
        fixture = json.loads(fixture)
        return self._add_links(fixture)

    def delete_link(self, link):
        " Delete a link on Database"
        l_uuid = self._db.hget('links_uuid', link)

        for tag in self.tags(l_uuid):
            if self._db.scard(tag) == 1:
                # Delete Tag if this link is the only reference
                self._db.delete(tag)
            else:
                # Delete link refered by tag
                self._db.srem(tag, l_uuid)

        self._db.hdel('links_uuid', link)
        self._db.delete(l_uuid)
        return True

    def get_links(self, *tags):
        """ Return a list of links filter by tags """
        # No tags : give all values
        if not tags:
            links = []
            for key in self._db.keys():
                if self._db.type(key) == b'hash' and key != b'links_uuid':
                    links.append(key.decode())
            return links
        # One tag : give all associate links
        if len(tags) == 1:
            return list(self._db.smembers(tags[0]))
        # Multi tags : give common links
        else:
            return list(self._db.sinter(tags))

    def sorted_links(self, *tags):
        """ Sorted links by priorities """
        links = {}
        for link in self.get_links(*tags):
            l = self._db.hgetall(link)
            if self.properties:
                links[l[b'name'].decode()] = l
            else:
                links[l[b'name'].decode()] = int(l[b'priority'])
        if self.properties:
            # Sorted by :
            # firstly "priority" (descending)
            # second "name"
            return OrderedDict(sorted(
                links.items(),
                key=lambda t: (- int(t[1][b'priority']), t[0]),
            )[:settings.NB_RESULTS])
        # Sorted by :
        # firstly "priority" (descending)
        # second "name"
        return OrderedDict(sorted(
            links.items(), key=lambda t: (- int(t[1]), t[0])
        )[:settings.NB_RESULTS])

    def dump(self):
        """ Serialize all fields on a json format string """
        links = {}
        for str_link in self.get_links():
            l = self._db.hgetall(str_link)
            links[l[b'name'].decode()] = {}
            link = links[l[b'name'].decode()]

            link['tags'] = self.tags(str_link)
            p = self._db.hgetall(str_link)
            link['real link'] = p[b"real link"].decode()
            link['title'] = p[b"title"].decode()
            link['priority'] = p[b"priority"].decode()
            link['description'] = p[b"description"].decode()
            link['init_date'] = p[b"init date"].decode()
            link['update_date'] = p[b"update date"].decode()
        return json.dumps(
            links, sort_keys=True, indent=4
        )

    def flush(self):
        """ Clear all DataBase's fields """
        return self._db.flushdb()

if settings.DB['ENGINE'] == 'redis':
    class DataBase(RedisDb):
        pass
