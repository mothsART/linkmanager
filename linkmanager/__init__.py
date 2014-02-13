# python2 "raw_input()" was renamed to input() on python3
try:
    input = raw_input
except NameError:
    pass

import readline
import json

import arrow
from clint.textui import puts, indent
from clint.textui.colored import green, red, white

from .settings import (TEST, INDENT)
from .translation import gettext as _
from . import validators
from .db import DataBase

__appname__ = 'LinkManager'
__author__ = "Ferry Jérémie <ferryjeremie@free.fr>"
__licence__ = "LGPL"
__version__ = '0.1'
VERSION = tuple(map(int, __version__.split('.')))


def test():
    return TEST


def preinput(label='', preinput=''):
    def hook():
        readline.insert_text(preinput)
        readline.redisplay()

    readline.set_pre_input_hook(hook)
    value = input(label)
    readline.set_pre_input_hook()
    return value


def properties_input(l, *properties):
    """
    Process to recover with input's functions :
    tags, priority value and a description associate with a link.
    """
    print(green(_('%s properties') % l + ' : ', bold=True))
    if len(properties[0]) > 1:
        tags = ', '.join(properties[0])
    else:
        tags = properties[0]
    tags = str(preinput(
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
    priority = preinput(
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
        priority = preinput(
            ' ' * INDENT
            + red(
                _(
                    'priority value not range '
                    'between 1 and 10, retry' + ' : '
                ),
                bold=True
            ),
            properties[1]
        )
    description = preinput(
        ' ' * INDENT
        + green(_('give a description') + ' : ', bold=True),
        properties[2]
    )
    return tags, priority, description


def _links_validator(links=None):
    """ Valid or not link list """
    if not links:
        links = input(
            _('Give one or several links (separate with space)') + ' : '
        )
        links = links.split()
    # keep only URLs that validate
    return [l for l in links if validators.URLValidator()(l)]


def addlinks(links=None):
    """ CMD: Add links to Database """
    links = _links_validator(links)
    fixture = {}
    db = DataBase(test=test())
    for l in links:
        properties = ([], '', '')
        if db.link_exist(l):
            update = input(
                ' ' * INDENT
                + red(
                    _(
                        'the link "%s" already exist: '
                        'do you want to update [Y/n] ? ' + ' : '
                    ) % l,
                    bold=True
                )
            )
            if update not in ['Y', '']:
                break
            properties = db.get_link_properties(l)
        tags, priority, description = properties_input(l, *properties)
        fixture[l] = {
            "tags": tags,
            "priority": priority,
            "description": description,
            "init date": str(arrow.now()),
            "update date": None
        }
    db.add_link(json.dumps(fixture))
    return True


def updatelink(links=None):
    """ CMD: Update a link on Database """
    links = _links_validator(links)
    fixture = {}
    db = DataBase(test=test())
    for l in links:
        properties = ([], '', '')
        if not db.link_exist(l):
            add = input(
                ' ' * INDENT
                + red(
                    _(
                        'the link "%s" does not exist: '
                        'do you want to create [Y/n] ? ' + ' : '
                    ) % l,
                    bold=True
                )
            )
            if add not in ['Y', '']:
                break
        else:
            properties = db.get_link_properties(l)
        tags, priority, description = properties_input(l, *properties)
        fixture[l] = {
            "tags": tags,
            "priority": priority,
            "description": description,
            #"init date": None,
            "update date": str(arrow.now())
        }
    db.add_link(json.dumps(fixture))
    return True

    # arrow.now()
    # arrow.get('...')


def removelink(links=None):
    """ CMD: Remove a link on Database """
    links = _links_validator(links)
    db = DataBase(test=test())
    is_removed = False
    for l in links:
        if db.delete_link(l):
            print(white(
                _('the link "%s" has been deleted.') % l,
                bold=True, bg_color='green'
            ))
            is_removed = True
        else:
            print(white(
                _('the link: "%s" does not exist.') % l,
                bold=True, bg_color='red'
            ))
    return is_removed


def flush(forced=['']):
    """ CMD: Purge the entire Database """
    if forced[0] == 'forced':
        flush_choice = ''
    else:
        flush_choice = input(white(
            _(
                "You're about to empty the entire Database."
                "Are you sure? [Y/n] ? "
            ),
            bold=True, bg_color='red'
        ))
    if flush_choice == _('Y') or flush_choice == '':
        if DataBase(test=test()).flush():
            print(white(
                _("Database entirely flushed."),
                bold=True, bg_color='green'
            ))
            return True
    return False


def load(json_files=None):
    """ CMD: Load a json file """
    if not json_files:
        print(white(
            _("No file to load."),
            bold=True, bg_color='red'
        ))
        return False
    for json_file in json_files:
        with open(json_file) as f:
            DataBase(test=test()).load(f.read())
    return True


def dump():
    """ CMD: return the serialization of all Database's fields """
    print(DataBase(test=test()).dump())
    return True


def searchlink(tags=None):
    """ CMD: Search links on Database filtering by tags """
    links = DataBase(test=test()).sorted_links(*tags)
    c_links = len(links)
    if c_links == 0:
        print(white(
            _('No links founded. '),
            bold=True, bg_color='red'
        ))
        return False
    if len(tags) == 0:
        print(
            white(
                '%s liens au total: ' % c_links,
                bold=True, bg_color='green'
            )
        )
    else:
        s_tags = '%s , '.join(tags)
        print(white(_(
            '%s liens correspondants aux tags : %s ') % (c_links, s_tags),
            bold=True, bg_color='green'
        ))
    with indent(INDENT):
        for l in links:
            puts(white(links[l]))
    return True
