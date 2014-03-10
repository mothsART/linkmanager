# encoding=utf8
# python2 "raw_input()" was renamed to input() on python3
try:
    input = raw_input
except NameError:
    pass

import readline
import json

import arrow
from clint.textui.colored import green, red, white

from .settings import (TEST, INDENT)
from .translation import gettext as _
from . import validators
from .db import DataBase


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

    def properties_input(self, l, *properties):
        """
        Process to recover with input's functions :
        tags, priority value and a description associate with a link.
        """
        print(green(_('%s properties') % l + ' : ', bold=True))
        if len(properties[0]) > 1:
            tags = ', '.join(properties[0])
        else:
            tags = properties[0]
        tags = str(self.preinput(
            ' ' * INDENT
            + green(
                _('tags (separate with ",")') + ' : ',
                bold=True
            ),
            tags
        ))
        if tags.find(',') == -1:
            tags = [tags]
        else:
            tags = tags.split(',')
        tags = [tag.strip() for tag in tags]
        priority = self.preinput(
            ' ' * INDENT
            + green(
                _('priority value (integer value between 1 and 10)') + ' : ',
                bold=True
            ),
            properties[1]
        )
        while True:
            if priority == '':
                priority = 1
            try:
                priority = int(priority)
                if priority > 0 and priority < 11:
                    break
            except:
                pass
            priority = self.preinput(
                ' ' * INDENT
                + red(
                    _(
                        'priority value not range '
                        'between 1 and 10, retry'
                    ) + ' : ',
                    bold=True
                ),
                properties[1]
            )
        description = self.preinput(
            ' ' * INDENT
            + green(_('give a description') + ' : ', bold=True),
            properties[2]
        )
        return tags, priority, description

    def _links_validator(self, links=None):
        """ Valid or not link list """
        if not links:
            links = input(
                _('Give one or several links (separate with space)') + ' : '
            )
            links = links.split()
        # keep only URLs that validate
        return [l for l in links if validators.URLValidator()(l)]

    def addlinks(self, links=None):
        """ CMD: Add links to Database """
        links = self._links_validator(links)
        fixture = {}
        db = DataBase(test=self.test)
        for l in links:
            properties = ([], '', '', str(arrow.now()), None)
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
                if update not in ['Y', '']:
                    continue
                properties = db.get_link_properties(l)
                properties = properties + (str(arrow.now()),)
            tags, priority, description = self.properties_input(l, *properties)
            fixture[l] = {
                "tags": tags,
                "priority": priority,
                "description": description,
                "init date": properties[3],
                "update date": properties[4]
            }
        db.add_link(json.dumps(fixture))
        return True

    def updatelinks(self, links=None):
        """ CMD: Update a link on Database """
        links = self._links_validator(links)
        fixture = {}
        db = DataBase(test=self.test)
        for l in links:
            properties = ([], '', '', str(arrow.now()), None)
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
                if add not in ['Y', '']:
                    continue
            else:
                properties = db.get_link_properties(l)
                properties = properties + (str(arrow.now()),)
            tags, priority, description = self.properties_input(l, *properties)
            fixture[l] = {
                "tags": tags,
                "priority": priority,
                "description": description,
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
                    "Are you sure [Y/n] ?"
                ) + " ",
                bold=True, bg_color='red'
            ))
        if flush_choice == _('Y') or flush_choice == '':
            if DataBase(test=self.test).flush():
                print(white(
                    _("Database entirely flushed."),
                    bold=True, bg_color='green'
                ))
                return True
        return False

    def load(self, json_files=None):
        """ CMD: Load a json file """
        if not json_files:
            print(white(
                _("No file to load."),
                bold=True, bg_color='red'
            ))
            return False
        db = DataBase(test=self.test)
        for json_file in json_files:
            with open(json_file) as f:
                db.load(f.read())
        return True

    def dump(self):
        """ CMD: return the serialization of all Database's fields """
        print(DataBase(test=self.test).dump())
        return True

    def searchlinks(self, tags=[]):
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
        for l in links:
            print(' ' * INDENT + white(l))
        return True
