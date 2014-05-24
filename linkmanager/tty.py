# -*- coding: utf-8 -*-
# python2 "raw_input()" was renamed to input() on python3
try:
    input = raw_input
except NameError:
    pass

import logging
import readline
import json

import arrow
from clint.textui.colored import green, red, white, yellow
import requests
from requests_futures.sessions import FuturesSession
from bs4 import BeautifulSoup

from .settings import (
    TEST, INDENT,
    MINIMIZE_URL, MINIMIZER, MINIMIZER_MIN_SIZE
)
from .translation import gettext as _
from . import validators
from .db import DataBase

logger = logging.getLogger()


class TTYInterface:
    test = TEST

    def preinput(self, label='', preinput=''):
        """ Pre-insert a text on a input function """
        def hook():
            readline.insert_text(preinput)
            readline.redisplay()

        readline.set_pre_input_hook(hook)
        value = input(label)
        readline.set_pre_input_hook()
        return value

    def properties_input(
        self, link, minimize_link,
        tags=[], priority=1, description='', date='', title=''
    ):
        """
        Process to recover with input's functions :
        tags, priority value and a description associate with a link.
        """
        session = FuturesSession()
        url = session.get(link)

        ### Enter tags
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

        if len(tags) > 1:
            new_tags = ' '.join(tags)
        else:
            new_tags = tags
        new_tags = str(self.preinput(
            ' ' * INDENT
            + green(
                _('tags (separate with spaces)') + ' :',
                bold=True
            ) + ' ',
            new_tags
        ))
        if new_tags.find(' ') == -1:
            new_tags = [new_tags]
        else:
            new_tags = new_tags.split()
        new_tags = [tag.strip() for tag in new_tags]

        ### Enter priority
        new_priority = self.preinput(
            ' ' * INDENT
            + green(
                _('priority value (integer value between 1 and 10)') + ' :',
                bold=True
            ) + ' ',
            priority
        )
        while True:
            if new_priority == '':
                new_priority = 1
            try:
                new_priority = int(new_priority)
                if new_priority > 0 and new_priority < 11:
                    break
            except:
                pass
            new_priority = self.preinput(
                ' ' * INDENT
                + red(
                    _(
                        'priority value not range '
                        'between 1 and 10, retry'
                    ) + ' : ',
                    bold=True
                ),
                priority
            )

        ### Enter description
        new_description = self.preinput(
            ' ' * INDENT
            + green(_('give a description') + ' : ', bold=True),
            description
        )
        # test if URL exist
        try:
            result = url.result()
            link = result.url
        except requests.exceptions.ConnectionError:
            result = None

        if title != '' and result:
            if result.status_code == 200:
                title = BeautifulSoup(result.content).title.string
        ### Enter title
        new_title = self.preinput(
            ' ' * INDENT
            + green(_('give a title') + ' : ', bold=True),
            title
        )
        ### Minimize URL if necessite
        if (
            MINIMIZE_URL and minimize_link == ''
            and len(link) > MINIMIZER_MIN_SIZE
        ):
            try:
                result = requests.get(MINIMIZER + link)
                minimize_link = result.content
            except requests.exceptions.ConnectionError:
                pass
        print(link, minimize_link)
        ### Cache websites

        return new_tags, new_priority, new_description, new_title

    def _links_validator(self, links=None):
        """ Valid or not link list """
        if not links:
            links = input(
                _('Give one or several links (separate with spaces)') + ' : '
            )
            links = links.split()
        # keep only URLs that validate
        return [l for l in links if validators.URLValidator()(l)]

    def addlinks(self, links=None, verbose=False):
        """ CMD: Add links to Database """
        links = self._links_validator(links)
        fixture = {}
        db = DataBase(test=self.test)
        for l in links:
            properties = ('', [], '', '', str(arrow.now()), None)
            if db.link_exist(l):
                update = input(
                    ' ' * INDENT
                    + red(
                        _(
                            'the link "%s" already exist: '
                            'do you want to update [Y/n] ?'
                        ) % l + ' : ',
                        bold=True
                    )
                )
                if update not in [_('Y'), '']:
                    continue
                properties = db.get_link_properties(l)
                properties = properties + (str(arrow.now()),)
            tags, priority, description, title = self.properties_input(
                l, *properties
            )
            fixture[l] = {
                "tags": tags,
                "priority": priority,
                "description": description,
                "title": title,
                "init date": properties[3],
                "update date": properties[4]
            }
        db.add_link(json.dumps(fixture))
        return True

    def updatelinks(self, links=None, verbose=False):
        """ CMD: Update a link on Database """
        links = self._links_validator(links)
        fixture = {}
        db = DataBase(test=self.test)
        for l in links:
            properties = ('', [], '', '', str(arrow.now()), None)
            if not db.link_exist(l):
                add = input(
                    ' ' * INDENT
                    + red(
                        _(
                            'the link "%s" does not exist: '
                            'do you want to create [Y/n] ?'
                        ) % l + ' : ',
                        bold=True
                    )
                )
                if add not in [_('Y'), '']:
                    continue
            else:
                properties = db.get_link_properties(l)
                properties = properties + (str(arrow.now()),)
            print(properties)
            tags, priority, description, title = self.properties_input(
                l, *properties
            )
            fixture[l] = {
                "tags": tags,
                "priority": priority,
                "description": description,
                "title": title,
                "init date": properties[3],
                "update date": properties[4]
            }
        db.add_link(json.dumps(fixture))
        return True

    def removelinks(self, links=None):
        """ CMD: Remove a link on Database """
        links = self._links_validator(links)
        db = DataBase(test=self.test)
        is_removed = False
        for l in links:
            if not db.link_exist(l):
                print(white(
                    _('the link "%s" does not exist.') % l,
                    bold=True, bg_color='red'
                ))
                continue
            if db.delete_link(l):
                print(white(
                    _('the link "%s" has been deleted.') % l,
                    bold=True, bg_color='green'
                ))
                is_removed = True
        return is_removed

    def flush(self, forced=['']):
        """ CMD: Purge the entire Database """
        if forced[0] == 'forced':
            flush_choice = ''
        else:
            flush_choice = input(white(
                _(
                    "You're about to empty the entire Database."
                ) + _(
                    "Are you sure [Y/n] ?"
                ),
                bold=True, bg_color='red'
            ) + " ")
        if flush_choice == _('Y') or flush_choice == '':
            if DataBase(test=self.test).flush():
                print(white(
                    _("Database entirely flushed."),
                    bold=True, bg_color='green'
                ))
                return True
        return False

    def load(self, json_files=None, verbose=False):
        """ CMD: Load a json file """
        if not json_files:
            print(white(
                _("No file to load."),
                bold=True, bg_color='red'
            ))
            return False
        db = DataBase(test=self.test)
        links = {}
        duplicates = []
        for json_file in json_files:
            with open(json_file) as f:
                fixture = json.loads(f.read())
            for link in fixture:
                if link in links:
                    if links[link] == fixture[link]:
                        continue
                    duplicates.append(
                        yellow(
                            _(
                                'Duplicate error '
                                + '(same link with different properties) :'
                            ),
                            bold=True, bg_color='red'
                        )
                        + ' ' + link
                    )
                links[link] = fixture[link]
        if duplicates != []:
            for d in set(duplicates):
                logger.error(d)
            return False
        db.load(json.dumps(links))
        return True

    def dump(self):
        """ CMD: return the serialization of all Database's fields """
        print(DataBase(test=self.test).dump())
        return True

    def searchlinks(self, tags=[], verbose=False):
        """ CMD: Search links on Database filtering by tags """
        d = DataBase(test=self.test)
        links = d.sorted_links(*tags)
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
        if verbose is True:
            nb_decade = int(len(str(len(links))))
            i = 0
            for l in links:
                i += 1
                index_space = nb_decade - int(len(str(i)))
                index_indent = ''
                if index_space:
                    index_indent = ' ' * index_space
                properties = d.get_link_properties(l)
                print(
                    ' ' * INDENT,
                    index_indent, '%d ➤' % i,
                    white(l, underline=True)
                )
                if properties['title']:
                    print(
                        '%s ├── %s : %s' % (
                            ' ' * INDENT * 2,
                            _('title'),
                            properties['title']
                        )
                    )
                print(
                    '%s ├── %s' % (
                        ' ' * INDENT * 2,
                        properties['l_uuid']
                    )
                )
                if l != properties['real link']:
                    print(
                        '%s ├── %s : %s' % (
                            ' ' * INDENT * 2,
                            _('URL complète'),
                            white(properties['real link'], underline=True)
                        )
                    )
                print(
                    '%s ├── %s : %s' % (
                        ' ' * INDENT * 2,
                        _('ordre de priorité'),
                        properties['priority']
                    )
                )
                print(
                    '%s ├── %s : %s' % (
                        ' ' * INDENT * 2,
                        _('tags'),
                        ' '.join(properties['tags'])
                    )
                )
                print(
                    '%s ├── %s : %s' % (
                        ' ' * INDENT * 2,
                        _('description'),
                        properties['description']
                    )
                )
                cd = arrow.get(properties['init_date'])
                create_date = _('create the %s at %s') % (
                    cd.format('DD MMMM YYYY'),
                    cd.format('HH:mm:ss')
                )
                if properties['update_date'] == 'None':
                    update_date = ' ' + _('and not updated yet.')
                else:
                    up = arrow.get(properties['update_date'])
                    update_date = _(' and update the %s at %s.') % (
                        up.format('DD MMMM YYYY'),
                        up.format('HH:mm:ss')
                    )
                date = create_date + update_date
                print(
                    '%s └── %s' % (
                        ' ' * INDENT * 2,
                        date
                    )
                )
        else:
            for l in links:
                print(' ' * INDENT + white(l))
        return True
