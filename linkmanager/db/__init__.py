import os
import json
import uuid
# import datetime
import logging
from collections import OrderedDict

import requests
from requests_futures.sessions import FuturesSession
from bs4 import BeautifulSoup
from clint.textui import progress
from clint.textui.colored import white, yellow

from linkmanager import settings
from linkmanager.translation import gettext as _

logger = logging.getLogger()


class MixinDb(object):
    """ Abstract DataBase Class """
    host = settings.DB['HOST']
    port = settings.DB['PORT']
    db_nb = settings.DB['DB_NB']
    properties = False

    def load(self, json_files=None, update_titles=True):
        """ Load a string : json format """
        if not json_files:
            print(white(
                _("No file to load."),
                bold=True, bg_color='red'
            ))
            return False

        links = {}
        errors = []
        for json_file in json_files:
            with open(json_file) as f:
                fixture = json.loads(f.read())
            for link in fixture:
                if link in links:
                    if links[link] == fixture[link]:
                        continue
                    errors.append(
                        yellow(
                            _(
                                'Duplicate error '
                                '(same link with different properties)'
                            ) + ' :',
                            bold=True, bg_color='red'
                        )
                        + ' ' + link
                    )
                if 'author' not in fixture[link]:
                    fixture[link]['author'] = ''
                if (
                    type(fixture[link]['tags']) != list
                    or fixture[link]['tags'] == []
                ):
                    errors.append(
                        yellow(
                            _(
                                'No affiliate tags'
                            ) + ' :',
                            bold=True, bg_color='red'
                        )
                        + ' ' + link
                    )
                links[link] = fixture[link]
        if errors != []:
            for e in set(errors):
                logger.error(e)
            return False

        if not update_titles:
            return self._add_links(links)

        # start_time = datetime.datetime.now()
        bar = progress.bar(range(len(links)))
        session = FuturesSession(max_workers=settings.WORKERS)

        urls = []
        for link in links:
            if 'title' in link:
                if link['title'] == '':
                    url = session.get(link)
                else:
                    url = link
            else:
                url = session.get(link)
            urls.append((url, link))
        for url in urls:
            title = ''
            if type(url) == str:
                next(bar)
                continue
            try:
                result = url[0].result()
            except:
                # 404 page
                next(bar)
                continue
            title = BeautifulSoup(result.content).title.string.strip()
            links.get(url[1])['title'] = title
            next(bar)

        # elsapsed_time = datetime.datetime.now() - start_time
        # print("Elapsed time: %ss" % elsapsed_time.total_seconds())
        return self._add_links(links)


class RedisDb(MixinDb):
    """ Redis DataBase """

    def __init__(self, test=False):
        """ Create a Redis DataBase """

        if test:
            import fakeredis
            self._db = fakeredis.FakeStrictRedis(
                host=self.host,
                port=self.port,
                db=self.db_nb
            )
        else:
            import redis
            self._db = redis.StrictRedis(
                host=self.host,
                port=self.port,
                db=self.db_nb
            )

    def __len__(self):
        """ Get nb of all stored links """
        return self._db.hlen('links_uuid')

    def _add_links(self, fixture):
        " Add links on Database"
        fixture = OrderedDict(sorted(fixture.items(), key=lambda t: t[0]))

        for real_link in fixture:
            value = fixture[real_link]
            # -- Minimize URL if necessite
            link = real_link
            if 'name' in value:
                link = value['name']
            if (
                settings.MINIMIZE_URL and link == real_link
                and len(real_link) > settings.MINIMIZER_MIN_SIZE
            ):
                try:
                    result = requests.get(settings.MINIMIZER + link)
                    link = result.content
                except requests.exceptions.ConnectionError:
                    pass

            if self._db.hexists('links_uuid', link):
                l_uuid = self._db.hget('links_uuid', link)
                # give a list of tags to removed on updating :
                # calculate difference between existing tags and new tags
                tags = set(self.tags(l_uuid.decode())) - set(value['tags'])
                for tag in tags:
                    if self._db.scard(tag) == 1:
                        # Delete Tag if this link is the only reference
                        self._db.delete(tag)
                    else:
                        # Delete link refered by tag
                        self._db.srem(tag, l_uuid.decode())
            else:
                l_uuid = str(uuid.uuid4())
                self._db.hset('links_uuid', link, l_uuid)

            for tag in value['tags']:
                for inc in range(len(tag)):
                    self._db.zadd(':compl', 0, tag[:inc])
                self._db.zadd(':compl', 0, tag + '*')
                if type(l_uuid) != str:
                    l_uuid = l_uuid.decode()
                self._db.sadd(tag, l_uuid)

            properties = {
                'name': link,
                'priority': value['priority'],
                'init date': value['init date'],
            }
            if link != real_link:
                properties['real_link'] = real_link

            if 'title' in value:
                properties['title'] = value['title']

            if 'update date' in value:
                if value['update date']:
                    properties['update date'] = value['update date']

            if 'description' in value:
                properties['description'] = value['description']

            author = os.getenv('USER')
            if hasattr(settings, 'AUTHOR'):
                author = settings.AUTHOR
            if 'author' in value:
                author = value['author']
            if author:
                properties['author'] = author
            self._db.hmset(l_uuid, properties)
        return True

    def get_link_properties(self, link):
        " Return all properties correspond to a link"
        properties = {}
        l_uuid = self._db.hget('links_uuid', link)
        properties['tags'] = self.tags(l_uuid.decode())
        p = self._db.hgetall(l_uuid)
        if b'real_link' in p:
            properties['real_link'] = p[b"real_link"].decode()
        if b'title' in p:
            properties['title'] = p[b"title"].decode()
        if b'author' in p:
            properties['author'] = p[b"author"].decode()
        properties['priority'] = p[b"priority"].decode()
        if b'description' in p:
            properties['description'] = p[b"description"].decode()
        properties['init date'] = p[b"init date"].decode()
        if b'update date' in p:
            properties['update date'] = p[b"update date"].decode()
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
        # -- TODO : perform scalability
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

    def delete_link(self, link):
        " Delete a link on Database"
        l_uuid = self._db.hget('links_uuid', link).decode()

        for tag in self.tags(l_uuid):
            if self._db.scard(tag) == 1:
                # Delete Tag if this link is the only reference
                self._db.delete(tag)
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
            if b"real_link" in p:
                link['real_link'] = p[b"real_link"].decode()
            if b'title' in p:
                if p[b"title"].decode() != '':
                    link['title'] = p[b"title"].decode()
            if b"author" in p:
                link['author'] = p[b"author"].decode()
            link['priority'] = p[b"priority"].decode()
            link['description'] = p[b"description"].decode()
            link['init date'] = p[b"init date"].decode()
            if b"update date" in p:
                link['update date'] = p[b"update date"].decode()
        return json.dumps(
            links, sort_keys=True, indent=4
        )

    def flush(self):
        """ Clear all DataBase's fields """
        return self._db.flushdb()

if settings.DB['ENGINE'] == 'redis':
    class DataBase(RedisDb):
        pass
