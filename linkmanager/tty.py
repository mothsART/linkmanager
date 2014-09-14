# -*- coding: utf-8 -*-
# python2 "raw_input()" was renamed to input() on python3
try:
    input = raw_input
except NameError:
    pass

import readline
import json

import arrow
from clint.textui.colored import green, red, white
from requests_futures.sessions import FuturesSession
from bs4 import BeautifulSoup

from . import settings, validators
from .translation import gettext as _
from .db import DataBase


class TTYInterface:
    def __init__(self, test=False):
        self.db = DataBase(test=test)

    def preinput(self, label='', preinput=''):
        """ Pre-insert a text on a input function """
        def hook():
            readline.insert_text(preinput)
            readline.redisplay()

        readline.set_pre_input_hook(hook)
        print(label, end='')
        value = input(' ')
        readline.set_pre_input_hook()
        return value

    def properties_input(self, link, **kwargs):
        """
        Process to recover with input's functions :
        tags, priority value and a description associate with a link.
        """
        title = ''
        if 'title' in kwargs:
            title = kwargs['title']
            url = None
        if title == '':
            url = FuturesSession().get(link)

        # -- Enter tags
        p = _('%s properties') % link
        begin_pos = p.find('http')
        end_pos = p[begin_pos:].find(' ')
        if end_pos == -1:
            end_pos = len(p)
        print(
            green(p[0:begin_pos], bold=True)
            + white(
                p[begin_pos:begin_pos + end_pos],
                bold=True, bg_color="green"
            )
            + green(p[begin_pos + end_pos:len(p)] + ' :', bold=True)
        )

        if len(kwargs['tags']) > 0:
            new_tags = ' '.join(kwargs['tags'])
        else:
            new_tags = ''
        new_tags = str(self.preinput(
            ' ' * settings.INDENT
            + green(
                _('tags (at least one, several separate with spaces)') + ' :',
                bold=True
            ),
            new_tags
        ))
        if new_tags.strip() == '':
            new_tags = []
        elif new_tags.find(' ') == -1:
            new_tags = [new_tags]
        else:
            new_tags = new_tags.split()
        new_tags = [tag.strip() for tag in new_tags]
        while True:
            if len(new_tags) >= 1:
                break
            new_tags = str(self.preinput(
                ' ' * settings.INDENT
                + red(
                    _('insert at least one tag (several separate with spaces)')
                    + ' :',
                    bold=True
                ) + ' ',
                new_tags
            ))

        # -- Enter priority
        new_priority = self.preinput(
            ' ' * settings.INDENT
            + green(
                _('priority value (integer value between 1 and 10)') + ' :',
                bold=True
            ),
            str(kwargs['priority'])
        )
        while True:
            try:
                new_priority = int(new_priority)
                if new_priority > 0 and new_priority < 11:
                    break
            except:
                pass
            new_priority = self.preinput(
                ' ' * settings.INDENT
                + red(
                    _(
                        'priority value not range '
                        'between 1 and 10, retry'
                    ) + ' :',
                    bold=True
                ),
                str(new_priority)
            )

        # -- Enter description
        new_description = self.preinput(
            ' ' * settings.INDENT
            + green(_('give a description') + ' :', bold=True),
            kwargs['description']
        )
        # test if URL exist
        try:
            result = url.result()
            link = result.url
        except:
            result = None

        if result:
            if result.status_code == 200:
                title = BeautifulSoup(result.content).title.string
        # -- Enter title
        new_title = self.preinput(
            ' ' * settings.INDENT
            + green(_('give a title') + ' :', bold=True),
            title
        )
        # -- Cache websites

        return new_tags, new_priority, new_description, new_title

    def _links_validator(self, links=None):
        """ Valid or not link list """
        if not links:
            print(
                _('Give one or several links (separate with spaces)') + ' :',
                end=''  # noqa
            )
            links = input(' ')
            links = links.split()
        # keep only URLs that validate
        return [l for l in links if validators.URLValidator()(l)]

    def addlinks(self, links=None, verbose=False):
        """ CMD: Add links to Database """
        links = self._links_validator(links)
        fixture = {}
        for l in links:
            properties = {
                'priority': 1,
                'init date': str(arrow.now()),
                'tags': [],
                'description': '',
                'title': ''
            }
            if self.db.link_exist(l):
                print(
                    ' ' * settings.INDENT
                    + red(
                        _(
                            'the link "%s" already exist: '
                            'do you want to update [Y/n] ?'
                        ) % l + ' :',
                        bold=True
                    )
                )
                update = input(' ')
                if update not in [_('Y'), '']:
                    continue
                properties = self.db.get_link_properties(l)
                properties['update date'] = str(arrow.now())
            tags, priority, description, title = self.properties_input(
                l, **properties
            )
            fixture[l] = {
                "tags": tags,
                "priority": priority,
                "description": description,
                "title": title,
                "init date": properties['init date']
            }
            if 'update date' in properties:
                fixture[l]['update date'] = properties['update date']
        self.db.add_link(json.dumps(fixture))
        return True

    def updatelinks(self, links=None, verbose=False):
        """ CMD: Update a link on Database """
        links = self._links_validator(links)
        fixture = {}
        for l in links:
            properties = {
                'priority': 1,
                'init date': str(arrow.now()),
                'update date': None,
                'tags': [],
                'description': '',
                'title': ''
            }
            if self.db.link_exist(l):
                properties = self.db.get_link_properties(l)
                properties['update date'] = str(arrow.now())
            else:
                add = print(
                    ' ' * settings.INDENT
                    + red(
                        _(
                            'the link "%s" does not exist: '
                            'do you want to create [Y/n] ?'
                        ) % l + ' : ',
                        bold=True
                    )
                )
                add = input(' ')
                if add not in [_('Y'), '']:
                    continue
            tags, priority, description, title = self.properties_input(
                l, **properties
            )
            fixture[l] = {
                "tags": tags,
                "priority": priority,
                "description": description,
                "title": title,
                "init date": properties['init date'],
                "update date": properties['update date']
            }
        self.db.add_link(json.dumps(fixture))
        return True

    def removelinks(self, links=None, verbose=False):
        """ CMD: Remove a link on Database """
        links = self._links_validator(links)
        is_removed = False
        for l in links:
            if not self.db.link_exist(l):
                print(white(
                    _('the link "%s" does not exist.') % l,
                    bold=True, bg_color='red'
                ))
                continue
            if self.db.delete_link(l):
                print(white(
                    _('the link "%s" has been deleted.') % l,
                    bold=True, bg_color='green'
                ))
                is_removed = True
        return is_removed

    def flush(self, forced=['']):
        """ CMD: Purge the entire Database """
        if forced[0] == 'forced':
            flush_choice = _('Y')
        else:
            print(white(
                _(
                    "You're about to empty the entire Database."
                ) + _(
                    "Are you sure [Y/n] ?"
                ),
                bold=True, bg_color='red'
            ), end='')  # noqa
            flush_choice = input(' ')
        if flush_choice == _('Y'):
            if self.db.flush():
                print(white(
                    _("Database entirely flushed."),
                    bold=True, bg_color='green'
                ))
                return True
        return False

    def load(self, json_files=None, verbose=False):
        """ CMD: Load a json file """
        return self.db.load(json_files)

    def dump(self):
        """ CMD: return the serialization of all Database's fields """
        print(self.db.dump())
        return True

    def suggest(self, value):
        """ Return a list of suggest tags """
        return self.db.complete_tags(value)

    def searchlinks(self, tags=[], verbose=False):
        """ CMD: Search links on Database filtering by tags """
        links = self.db.sorted_links(*tags)
        c_links = len(links)
        if c_links == 0:
            print(white(
                _('No links founded') + '. ',
                bold=True, bg_color='red'
            ))
            return False
        if len(tags) == 0:
            print(
                white(
                    _('%s links totally founded') % c_links + ' : ',
                    bold=True, bg_color='green'
                )
            )
        else:
            print(white(
                _('%s links founded') % c_links + ' : ',
                bold=True, bg_color='green'
            ))
        nb_decade = int(len(str(len(links))))
        i = 0
        for l in links:
            i += 1
            index_space = nb_decade - int(len(str(i)))
            index_indent = ''
            if index_space:
                index_indent = ' ' * index_space
            properties = self.db.get_link_properties(l)
            print(
                ' ' * settings.INDENT,
                index_indent, '%d ➤' % i,
                white(l, underline=True)
            )
            if 'title' in properties:
                decoration = '└──'
                if verbose:
                    decoration = '├──'
                print(
                    '%s %s %s : %s' % (
                        ' ' * settings.INDENT * 2,
                        decoration,
                        _('Title'),
                        properties['title']
                    )
                )
            if not verbose:
                continue
            print(
                '%s ├── %s' % (
                    ' ' * settings.INDENT * 2,
                    properties['l_uuid']
                )
            )
            if 'real_link' in properties:
                print(
                    '%s ├── %s : %s' % (
                        ' ' * settings.INDENT * 2,
                        _('Complete URL'),
                        white(properties['real_link'], underline=True)
                    )
                )
            print(
                '%s ├── %s : %s' % (
                    ' ' * settings.INDENT * 2,
                    _('Priority order'),
                    properties['priority']
                )
            )
            print(
                '%s ├── %s : %s' % (
                    ' ' * settings.INDENT * 2,
                    _('Tags'),
                    ' '.join(properties['tags'])
                )
            )
            if 'description' in properties:
                print(
                    '%s ├── %s : %s' % (
                        ' ' * settings.INDENT * 2,
                        _('Description'),
                        properties['description']
                    )
                )
            if 'author' in properties:
                print(
                    '%s ├── %s : %s' % (
                        ' ' * settings.INDENT * 2,
                        _('Author'),
                        white(properties['author'])
                    )
                )
            cd = arrow.get(properties['init date'])
            create_date = _('create the {date} at {hour}').format(
                date=cd.format('DD MMMM YYYY'),
                hour=cd.format('HH:mm:ss')
            )
            update_date = ' ' + _('and not updated yet.')
            if 'update date' in properties:
                up = arrow.get(properties['update date'])
                update_date = _(' and update the {date} at {hour}.').format(
                    date=up.format('DD MMMM YYYY'),
                    hour=up.format('HH:mm:ss')
                )
            date = create_date + update_date
            print(
                '%s └── %s' % (
                    ' ' * settings.INDENT * 2,
                    date
                )
            )
        return True
