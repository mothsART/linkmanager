#!/usr/bin/env python

# pip install argcomplete
import argcomplete
import argparse

from linkmanager.translation import gettext as _
from linkmanager import (
    addlink, updatelink, deletelink, searchlink
)

green = '\033[0;32m'


def color(c_str, color='\033[1;42m'):
    return '{color}{c_str}{cb}'.format(color=color, c_str=c_str, cb='\033[1;m')

choices = {
    'add': ['a', 'add', _('add a link'), addlink],
    'udpate': ['u', 'update', _('update a link'), updatelink],
    'delete': ['d', 'delete', _('delete a link'), deletelink],
    'search': ['s', 'search', _('search a link on database'), searchlink]
}


class Choices(object):
    short_cmd = [v[0] for v in choices.values()]
    long_cmd = [v[1] for v in choices.values()]

    @classmethod
    def cmd(cls):
        return cls.short_cmd + cls.long_cmd

    @classmethod
    def call(cls, choice):
        for c in choices.values():
            if c[0] == choice or c[1] == choice:
                return c[3]

    @staticmethod
    def descriptions():
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
    description='Manage your Links and and never lose them...'
)
parser.add_argument(
    'choice',
    choices=Choices.cmd()
)
parser.add_argument(
    'value', nargs='*'
)
argcomplete.autocomplete(parser)
args = parser.parse_args()
args = vars(args)

try:
    Choices.call(args['choice'])(args['value'])
except KeyboardInterrupt:
    print('\nCtrl + C interruption')
    pass
