#!/usr/bin/env python

import argcomplete
import argparse

from linkmanager.translation import gettext as _
from linkmanager import (
    addlinks, updatelinks, removelinks,
    flush, load, dump,
    searchlinks
)

choices = {
    'add': ['a', 'add', _('add links'), addlinks],
    'udpate': ['u', 'update', _('update links'), updatelinks],
    'remove': ['r', 'remove', _('remove links'), removelinks],
    'flush': ['f', 'flush', _('flush the entire database'), flush],
    'load': ['l', 'load', _('load a json database file'), load],
    'dump': ['d', 'dump', _('dump all database to a json file'), dump],
    'search': ['s', 'search', _('search links on database'), searchlinks]
}


class Choices(object):
    """ LinkManager choices """
    short_cmd = [v[0] for v in choices.values()]
    long_cmd = [v[1] for v in choices.values()]

    @classmethod
    def cmd(cls):
        """ Return a list of LinkManager choices """
        return cls.short_cmd + cls.long_cmd

    @classmethod
    def call(cls, choice):
        """ Call the good sub-command """
        for c in choices.values():
            if c[0] == choice or c[1] == choice:
                return c[3]

    @staticmethod
    def descriptions():
        """ Help give short and long command and her description """
        description = [
            '\n'
            + _('Choices supports the following: (short cmd/cmd)')
            + '\n'
        ]
        max_size = max([max(len(v[0]), len(v[1])) for v in choices.values()])
        for c in choices:
            spaces = ' ' * (
                4 + max_size - len(choices[c][0]) - len(choices[c][1])
            )
            description.append(
                '    {cmd} / {long_cmd}{spaces}  - {help}\n'.format(
                    cmd=choices[c][0], long_cmd=choices[c][1],
                    spaces=spaces, help=choices[c][2]
                )
            )
        return ''.join(description)


parser = argparse.ArgumentParser(
    formatter_class=argparse.RawTextHelpFormatter,
    epilog=Choices.descriptions(),
    description=_('Manage your Links ...')
)
parser.add_argument(
    'choice',
    choices=Choices.cmd()
)
parser.add_argument(
    '-f', '--forced', help=_('force command to be quiet and without input'),
    default=False, action='store_const', const='forced'
)
parser.add_argument(
    'value', nargs='*'
)
argcomplete.autocomplete(parser)
args = parser.parse_args()
args = vars(args)

try:
    f_name = Choices.call(args['choice']).__name__
    if f_name == 'flush':
        Choices.call(args['choice'])(args['value'] + [args['forced']])
    elif f_name == 'dump':
        Choices.call(args['choice'])()
    else:
        Choices.call(args['choice'])(args['value'])
except KeyboardInterrupt:
    print('\n' + _('Ctrl + C interruption'))
