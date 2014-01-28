import operator
import json
import uuid
from linkmanager import settings


class RedisDb(object):
    host = 'localhost'
    port = 6379
    db_nb = 0

    def __init__(self, conf=None):
        import redis
        if conf:
            self.host = conf.host
            self.port = conf.port
            self.db_nb = conf.db_nb
        self._db = redis.StrictRedis(
            host=self.host,
            port=self.port,
            db=self.db_nb
        )

    def get_links(self, *tags):
        # No tags : give all values
        if not tags:
            links = []
            for key in self._db.keys():
                if self._db.type(key) == b'hash' and key != b'links_uuid':
                    links.append(key)
            return links
        # One tag : give all associate links
        if len(tags) == 1:
            return self._db.smembers(tags[0])
        # Multi tags : give common links
        else:
            return self._db.sinter(tags)

    def sort_by_priority(self, links):
        links_priority = {}
        for l in links:
            links_priority[l] = self._db.zrank('links_priority', l)
        links_priority = sorted(
            links_priority.items(),
            key=operator.itemgetter(1),
            reverse=True
        )
        if settings.NB_RESULTS == -1:
            return links_priority
        return links_priority[:settings.NB_RESULTS]

    def get_properties(self, link=None):
        return self._db.hgetall(link)

    def load(self, fixture):
        fixture = json.loads(fixture)
        for link in fixture:
            value = fixture[link]

            if self._db.hexists('links_uuid', link):
                l_uuid = self._db.hget('links_uuid', link)
            else:
                l_uuid = str(uuid.uuid1())
                self._db.hset('links_uuid', link, l_uuid)

            for tag in value['tags']:
                self._db.sadd(tag, l_uuid)

            self._db.zadd('links_priority', value['priority'], l_uuid)
            self._db.hmset(
                l_uuid,
                {
                    'name': link,
                    'description': value['description'],
                    'init date': value['init date'],
                    'update date': value['update date']
                }
            )
        return True

    def dump(self):
        print(self.get_links())

    def flush(self):
        self._db.flushdb()

if settings.DB == 'redis':
    class DataBase(RedisDb):
        pass
