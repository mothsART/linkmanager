import redis
import json
import uuid
from collections import OrderedDict

from linkmanager import settings


class RedisDb(object):
    """ Redis DataBase """
    host = settings.DB['HOST']
    port = settings.DB['PORT']
    db_nb = settings.DB['DB_NB']
    properties = False

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
                self._db.sadd(tag, l_uuid)

            self._db.hmset(
                l_uuid,
                {
                    'name': link,
                    'priority': value['priority'],
                    'description': value['description'],
                    'init date': value['init date'],
                    'update date': value['update date']
                }
            )
        return True

    def get_link_properties(self, link):
        l_uuid = self._db.hget('links_uuid', link)
        tags = self.tags(l_uuid)
        p = self._db.hgetall(l_uuid)
        priority = p[b"priority"].decode()
        description = p[b"description"].decode()
        init_date = p[b"init date"].decode()
        return tags, priority, description, init_date

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

    def load(self, fixture):
        """ Load a string : json format """
        fixture = json.loads(fixture)
        return self._add_links(fixture)

    def dump(self):
        """ Serialize all fields on a json format string """
        links = {}
        for tag in self.tags():
            members = self._db.smembers(tag)
            for m in members:
                if m in links:
                    links[m]["tags"].add(tag)
                else:
                    links[m] = {"tags": set([tag])}
        dump_links = {}
        for l in links:
            p = self._db.hgetall(l)
            tags = sorted(links[l]["tags"])
            dump_links[p[b'name'].decode()] = {
                "tags": tags,
                "priority": p[b"priority"].decode(),
                "description": p[b"description"].decode(),
                "init date": p[b"init date"].decode(),
                "update date": p[b"update date"].decode()
            }
        return json.dumps(
            dump_links, sort_keys=True, indent=4
        )

    def flush(self):
        """ Clear all DataBase's fields """
        return self._db.flushdb()

if settings.DB['ENGINE'] == 'redis':
    class DataBase(RedisDb):
        pass
