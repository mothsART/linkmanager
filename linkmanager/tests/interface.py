import json
from io import StringIO
from unittest.mock import (patch, mock_open)

from linkmanager.settings import INDENT
from linkmanager import (
    flush, addlinks,
    load, dump
)
from linkmanager.translation import gettext as _


class CP(object):
    result = ''

    def cpvar(self, r):
        self.result = r

cp = CP()

addlink = iter([
    # input on: test_cmd_flush
    _('Y'),
    _('n'),

    # input on: test_cmd_addlinks
    'http://link1.com http://link2.com http://link3.com',
    'link1_tag1, link1_tag2, link1_tag3',
    '',
    'link_1 description...',

    'link2_tag1, link2_tag2',
    5,
    'link_2 description...',

    'link3_tag1',
    'incorrect priority value',
    15,
    5,
    'link_3 description...'
])


def get_input(string):
    print(string)
    return next(addlink)


@patch('linkmanager.test', lambda: True)
@patch('builtins.input', get_input)
@patch('sys.stdout', new_callable=StringIO)
def test_cmd_flush(mock_stdout):
    assert flush() is True
    assert mock_stdout.getvalue() == ''.join([
        "You're about to empty the entire Database.",
        "Are you sure? [Y/n] ? \n",
        "Database entirely flushed.\n"
    ])
    mock_stdout.truncate(0)
    mock_stdout.seek(0)
    assert flush() is False
    assert mock_stdout.getvalue() == ''.join([
        "You're about to empty the entire Database.",
        "Are you sure? [Y/n] ? \n"
    ])


@patch('linkmanager.test', lambda: True)
@patch('builtins.input', get_input)
@patch('sys.stdout', new_callable=StringIO)
@patch('arrow.now', lambda: "2014-02-10T19:59:34.612714+01:00")
def test_cmd_addlinks(mock_stdout):
    flush(forced=['forced'])
    assert mock_stdout.getvalue() == _('Database entirely flushed.') + '\n'

    mock_stdout.seek(0)
    assert addlinks() is True
    cp.cpvar(mock_stdout.getvalue())

    assert mock_stdout.getvalue() == ''.join([
        _('Give one or several links (separate with space)'), ' : \n',
        _('%s properties') % 'http://link1.com', ' : \n',
        ' ' * INDENT, _('tags (separate with ",")'), ' : \n',
        ' ' * INDENT, _('priority value (integer value between 1 and 10)'),
        ' : \n',
        ' ' * INDENT, _('give a description'), ' : \n',

        _('%s properties') % 'http://link2.com', ' : \n',
        ' ' * INDENT, _('tags (separate with ",")'), ' : \n',
        ' ' * INDENT, _('priority value (integer value between 1 and 10)'),
        ' : \n',
        ' ' * INDENT, _('give a description'), ' : \n',

        _('%s properties') % 'http://link3.com', ' : \n',
        ' ' * INDENT, _('tags (separate with ",")'), ' : \n',
        ' ' * INDENT, _('priority value (integer value between 1 and 10)'),
        ' : \n',
        ' ' * INDENT, _('priority value not range between 1 and 10, retry'),
        ' : \n',
        ' ' * INDENT, _('priority value not range between 1 and 10, retry'),
        ' : \n',
        ' ' * INDENT, _('give a description'), ' : \n'
    ])

dump_afteradd = """{
    "http://link1.com": {
        "description": "link_1 description...",
        "init date": "2014-02-10T19:59:34.612714+01:00",
        "priority": "1",
        "tags": [
            "link1_tag1",
            "link1_tag2",
            "link1_tag3"
        ],
        "update date": "None"
    },
    "http://link2.com": {
        "description": "link_2 description...",
        "init date": "2014-02-10T19:59:34.612714+01:00",
        "priority": "5",
        "tags": [
            "link2_tag1",
            "link2_tag2"
        ],
        "update date": "None"
    },
    "http://link3.com": {
        "description": "link_3 description...",
        "init date": "2014-02-10T19:59:34.612714+01:00",
        "priority": "5",
        "tags": [
            "link3_tag1"
        ],
        "update date": "None"
    }
}
"""


@patch('linkmanager.test', lambda: True)
@patch('sys.stdout', new_callable=StringIO)
def test_cmd_dump(mock_stdout):
# def test_cmd_dump():
#     with open('tt.json', 'w') as f:
#         f.write(cp.result)
#     assert False is True
    assert dump() is True
    assert json.loads(mock_stdout.getvalue()) == json.loads(dump_afteradd)


@patch('linkmanager.test', lambda: True)
@patch('sys.stdout', new_callable=StringIO)
def test_cmd_load_null(mock_stdout):
    flush(forced=['forced'])
    assert mock_stdout.getvalue() == _('Database entirely flushed.') + '\n'

    mock_stdout.truncate(0)
    mock_stdout.seek(0)
    # No file to load
    assert load() is False
    assert mock_stdout.getvalue() == 'No file to load.\n'


first_fixture = """{
    "http://linuxfr.org": {
        "description": "fr community ",
        "init date": "2014-01-27T17:45:19.985742+00:00",
        "priority": "8",
        "tags": [
            "bsd",
            "gnu",
            "linux"
        ],
        "update date": "2014-01-27T17:55:19.985742+00:00"
    },
    "http://phoronix.com": {
        "description": "OS benchmarkin",
        "init date": "2014-01-27T17:57:19.985742+00:00",
        "priority": "5",
        "tags": [
            "benchmark",
            "linux"
        ],
        "update date": "None"
    },
    "http://ubuntu.com": {
        "description": "Fr Ubuntu site",
        "init date": "2014-01-27T17:37:19.985742+00:00",
        "priority": "10",
        "tags": [
            "linux",
            "python",
            "shell",
            "ubuntu"
        ],
        "update date": "None"
    }
}
"""


@patch('linkmanager.test', lambda: True)
@patch('builtins.open', mock_open(read_data=first_fixture))
def test_cmd_one_load():
    flush(forced=['forced'])
    # One file
    assert load(['file.json']) is True


@patch('linkmanager.test', lambda: True)
@patch('sys.stdout', new_callable=StringIO)
def test_cmd_dump_after_one_load(mock_stdout):
    dump()
    assert json.loads(mock_stdout.getvalue()) == json.loads(first_fixture)


second_fixture = """{
    "http://phoronix.com": {
        "description": "OS benchmarkin",
        "init date": "2014-01-27T17:57:19.985742+00:00",
        "priority": "5",
        "tags": [
            "benchmark",
            "linux"
        ],
        "update date": "None"
    }
}
"""
third_fixture = """{
    "http://ubuntu.com": {
        "description": "Fr Ubuntu site",
        "init date": "2014-01-27T17:37:19.985742+00:00",
        "priority": "10",
        "tags": [
            "linux",
            "python",
            "shell",
            "ubuntu"
        ],
        "update date": "None"
    }
}
"""

fourth_fixture = """{
    "http://phoronix.com": {
        "description": "OS benchmarkin",
        "init date": "2014-01-27T17:57:19.985742+00:00",
        "priority": "5",
        "tags": [
            "benchmark",
            "linux"
        ],
        "update date": "None"
    },
    "http://ubuntu.com": {
        "description": "Fr Ubuntu site",
        "init date": "2014-01-27T17:37:19.985742+00:00",
        "priority": "10",
        "tags": [
            "linux",
            "python",
            "shell",
            "ubuntu"
        ],
        "update date": "None"
    }
}

"""
files = iter([second_fixture, third_fixture])


@patch('linkmanager.test', lambda: True)
@patch('builtins.open', mock_open(read_data=next(files)))
def test_cmd_multi_load():
    flush(forced=['forced'])
    # Several files
    assert load(['file_1.json', 'file_2.json']) is True


@patch('linkmanager.test', lambda: True)
@patch('sys.stdout', new_callable=StringIO)
def test_cmd_dump_after_multi_load(mock_stdout):
    assert dump() is True
    assert json.loads(mock_stdout.getvalue()) != json.loads(fourth_fixture)
