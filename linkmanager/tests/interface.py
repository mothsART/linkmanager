import json
from io import StringIO
from unittest.mock import (patch, mock_open, MagicMock)

from linkmanager.settings import INDENT
from linkmanager import interface
tty_i = interface()
tty_i.test = True

from linkmanager.translation import gettext as _


class CP(object):
    result = ''

    def cpvar(self, r):
        self.result = r

cp = CP()

addlink = iter([
    ### input on: test_cmd_flush
    _('Y'),
    _('n'),

    ### input on: test_cmd_addlinks
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
    'link_3 description...',

    ### input on: test_cmd_addlinks_with_update
    'http://link2.com http://link3.com http://link4.com',
    _('n'),
    # like Yes
    '',
    'link3_tag1, link3_tag2, link3_tag3',
    7,
    'link_3 description...',

    'link4_tag1',
    8,
    'link_4 description...',

    ### input on: test_cmd_updatelinks
    'http://link1.com',
    'link1_tag1, link1_tag3, link1_tag4',
    2,
    'link_1 description...',

    ### input on: test_cmd_updatelinks_with_add
    'http://link3.com http://link5.com http://link6.com',
    'link3_tag1, link3_tag2, link3_tag3',
    10,
    'link_3 new description...',

    _('n'),
    _('Y'),
    'link6_tag1, link6_tag2, link6_tag3',
    9,
    'link_6 description...',

    ### input on: test_cmd_removelinks
    ''
])


def get_input(string):
    print(string)
    return next(addlink)


@patch('builtins.input', get_input)
@patch('sys.stdout', new_callable=StringIO)
def test_cmd_flush(mock_stdout):
    assert tty_i.flush() is True
    assert mock_stdout.getvalue() == ''.join([
        _("You're about to empty the entire Database."),
        _("Are you sure [Y/n] ?") + " \n",
        _("Database entirely flushed.") + "\n"
    ])
    mock_stdout.truncate(0)
    mock_stdout.seek(0)
    assert tty_i.flush() is False
    assert mock_stdout.getvalue() == ''.join([
        _("You're about to empty the entire Database."),
        _("Are you sure [Y/n] ?") + " \n"
    ])


@patch('builtins.input', get_input)
@patch('sys.stdout', new_callable=StringIO)
@patch('arrow.now', lambda: "2014-02-10T19:59:34.612714+01:00")
def test_cmd_addlinks(mock_stdout):
    tty_i.flush(forced=['forced'])
    assert mock_stdout.getvalue() == _('Database entirely flushed.') + '\n'

    mock_stdout.seek(0)
    assert tty_i.addlinks() is True

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


@patch('builtins.input', get_input)
@patch('sys.stdout', new_callable=StringIO)
@patch('arrow.now', lambda: "2014-02-14T10:22:34.612714+01:00")
def test_cmd_addlinks_with_update(mock_stdout):
    assert tty_i.addlinks() is True

    assert mock_stdout.getvalue() == ''.join([
        _('Give one or several links (separate with space)'), ' : \n',

        ' ' * INDENT, _(
            'the link "%s" already exist: '
            'do you want to update [Y/n] ?'
        ) % 'http://link2.com', ' : \n',

        ' ' * INDENT, _(
            'the link "%s" already exist: '
            'do you want to update [Y/n] ?'
        ) % 'http://link3.com', ' : \n',
        _('%s properties') % 'http://link3.com', ' : \n',
        ' ' * INDENT, _('tags (separate with ",")'), ' : \n',
        ' ' * INDENT, _('priority value (integer value between 1 and 10)'),
        ' : \n',
        ' ' * INDENT, _('give a description'), ' : \n',

        _('%s properties') % 'http://link4.com', ' : \n',
        ' ' * INDENT, _('tags (separate with ",")'), ' : \n',
        ' ' * INDENT, _('priority value (integer value between 1 and 10)'),
        ' : \n',
        ' ' * INDENT, _('give a description'), ' : \n',
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
        "priority": "7",
        "tags": [
            "link3_tag1",
            "link3_tag2",
            "link3_tag3"
        ],
        "update date": "2014-02-14T10:22:34.612714+01:00"
    },
    "http://link4.com": {
        "description": "link_4 description...",
        "init date": "2014-02-14T10:22:34.612714+01:00",
        "priority": "8",
        "tags": ["link4_tag1"],
        "update date": "None"
    }
}
"""


@patch('sys.stdout', new_callable=StringIO)
def test_cmd_addlinks_dump(mock_stdout):
    assert tty_i.dump() is True
    assert json.loads(mock_stdout.getvalue()) == json.loads(dump_afteradd)


@patch('builtins.input', get_input)
@patch('sys.stdout', new_callable=StringIO)
@patch('arrow.now', lambda: "2014-02-15T12:20:34.612714+01:00")
def test_cmd_updatelinks(mock_stdout):
    assert tty_i.updatelinks() is True

    assert mock_stdout.getvalue() == ''.join([
        _('Give one or several links (separate with space)'), ' : \n',

        _('%s properties') % 'http://link1.com', ' : \n',
        ' ' * INDENT, _('tags (separate with ",")'), ' : \n',
        ' ' * INDENT, _('priority value (integer value between 1 and 10)'),
        ' : \n',
        ' ' * INDENT, _('give a description'), ' : \n'
    ])


@patch('builtins.input', get_input)
@patch('sys.stdout', new_callable=StringIO)
@patch('arrow.now', lambda: "2014-02-10T19:59:34.612714+01:00")
def test_cmd_updatelinks_with_add(mock_stdout):
    assert tty_i.updatelinks() is True
    #cp.cpvar(mock_stdout.getvalue())

    assert mock_stdout.getvalue() == ''.join([
        _('Give one or several links (separate with space)'), ' : \n',

        _('%s properties') % 'http://link3.com', ' : \n',
        ' ' * INDENT, _('tags (separate with ",")'), ' : \n',
        ' ' * INDENT, _('priority value (integer value between 1 and 10)'),
        ' : \n',
        ' ' * INDENT, _('give a description'), ' : \n',

        ' ' * INDENT, _(
            'the link "%s" does not exist: '
            'do you want to create [Y/n] ?'
        ) % 'http://link5.com', ' : \n',

        ' ' * INDENT, _(
            'the link "%s" does not exist: '
            'do you want to create [Y/n] ?'
        ) % 'http://link6.com', ' : \n',

        _('%s properties') % 'http://link6.com', ' : \n',
        ' ' * INDENT, _('tags (separate with ",")'), ' : \n',
        ' ' * INDENT, _('priority value (integer value between 1 and 10)'),
        ' : \n',
        ' ' * INDENT, _('give a description'), ' : \n'
    ])


dump_afterupdate = """{
    "http://link1.com": {
        "description": "link_1 description...",
        "init date": "2014-02-10T19:59:34.612714+01:00",
        "priority": "2",
        "tags": [
            "link1_tag1",
            "link1_tag3",
            "link1_tag4"
        ],
        "update date": "2014-02-15T12:20:34.612714+01:00"
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
        "description": "link_3 new description...",
        "init date": "2014-02-10T19:59:34.612714+01:00",
        "priority": "10",
        "tags": [
            "link3_tag1",
            "link3_tag2",
            "link3_tag3"
        ],
        "update date": "2014-02-10T19:59:34.612714+01:00"
    },
    "http://link4.com": {
        "description": "link_4 description...",
        "init date": "2014-02-14T10:22:34.612714+01:00",
        "priority": "8",
        "tags": [
            "link4_tag1"
        ],
        "update date": "None"
    },
    "http://link6.com": {
        "description": "link_6 description...",
        "init date": "2014-02-10T19:59:34.612714+01:00",
        "priority": "9",
        "tags": [
            "link6_tag1",
            "link6_tag2",
            "link6_tag3"
        ],
        "update date": "None"
    }
}
"""


@patch('sys.stdout', new_callable=StringIO)
def test_cmd_updatelinks_dump(mock_stdout):
# def test_cmd_updatelinks_dump():
    # with open('tt.json', 'w') as f:
    #     f.write(cp.result)
    # assert False is True
    assert tty_i.dump() is True
    assert json.loads(mock_stdout.getvalue()) == json.loads(dump_afterupdate)


@patch('builtins.input', get_input)
@patch('sys.stdout', new_callable=StringIO)
def test_cmd_removelinks(mock_stdout):
    assert tty_i.removelinks() is False
    assert tty_i.removelinks([
        "http://link5.com",
        "http://link6.com",
        "http://link7.com"
    ]) is True
    assert mock_stdout.getvalue() == ''.join([
        _('Give one or several links (separate with space)'), ' : \n',
        _('the link "%s" does not exist.') % "http://link5.com" + '\n',
        _('the link "%s" has been deleted.') % "http://link6.com" + '\n',
        _('the link "%s" does not exist.') % "http://link7.com" + '\n'
    ])


dump_afterremove = """{
    "http://link1.com": {
        "description": "link_1 description...",
        "init date": "2014-02-10T19:59:34.612714+01:00",
        "priority": "2",
        "tags": [
            "link1_tag1",
            "link1_tag3",
            "link1_tag4"
        ],
        "update date": "2014-02-15T12:20:34.612714+01:00"
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
        "description": "link_3 new description...",
        "init date": "2014-02-10T19:59:34.612714+01:00",
        "priority": "10",
        "tags": [
            "link3_tag1",
            "link3_tag2",
            "link3_tag3"
        ],
        "update date": "2014-02-10T19:59:34.612714+01:00"
    },
    "http://link4.com": {
        "description": "link_4 description...",
        "init date": "2014-02-14T10:22:34.612714+01:00",
        "priority": "8",
        "tags": [
            "link4_tag1"
        ],
        "update date": "None"
    }
}
"""


@patch('sys.stdout', new_callable=StringIO)
def test_cmd_removelinks_dump(mock_stdout):
    assert tty_i.dump() is True
    assert json.loads(mock_stdout.getvalue()) == json.loads(dump_afterremove)


@patch('sys.stdout', new_callable=StringIO)
def test_cmd_load_null(mock_stdout):
    tty_i.flush(forced=['forced'])
    assert mock_stdout.getvalue() == _('Database entirely flushed.') + '\n'

    mock_stdout.truncate(0)
    mock_stdout.seek(0)
    # No file to load
    assert tty_i.load() is False
    assert mock_stdout.getvalue() == _('No file to load.') + '\n'


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


@patch('builtins.open', mock_open(read_data=first_fixture))
def test_cmd_one_load():
    tty_i.flush(forced=['forced'])
    # One file
    assert tty_i.load(['file.json']) is True


@patch('sys.stdout', new_callable=StringIO)
def test_cmd_dump_after_one_load(mock_stdout):
    tty_i.dump()
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
    "http://xkcd.com": {
        "description": "A webcomic of romance ...",
        "init date": "2014-02-06T17:37:19.985742+00:00",
        "priority": "5",
        "tags": [
            "bsd",
            "joke",
            "linux",
            "math"
        ],
        "update date": "None"
    }
}
"""

fifth_fixture = """{
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
    },
    "http://xkcd.com": {
        "description": "A webcomic of romance ...",
        "init date": "2014-02-06T17:37:19.985742+00:00",
        "priority": "5",
        "tags": [
            "bsd",
            "joke",
            "linux",
            "math"
        ],
        "update date": "None"
    }
}
"""

files = iter([second_fixture, third_fixture, fourth_fixture])


def multi_mock_open(mock=None, read_data=''):
    """
    Inspiration by the mock_open function and
    http://stackoverflow.com/questions/9349122/python-mock-mocking-several-open
    """
    import _io
    file_spec = list(set(dir(_io.TextIOWrapper)).union(set(dir(_io.BytesIO))))

    if mock is None:
        mock = MagicMock(name='open', spec=open)

    handle = MagicMock(spec=file_spec)
    handle.write.return_value = None
    handle.__enter__.return_value = handle
    handle.read.side_effect = lambda: next(files)

    mock.return_value = handle
    return mock


@patch('builtins.open', multi_mock_open())
def test_cmd_multi_load():
    tty_i.flush(forced=['forced'])
    # Several files
    assert tty_i.load(json_files=[
        'file_1.json', 'file_2.json', 'file_3.json'
    ]) is True


@patch('sys.stdout', new_callable=StringIO)
def test_cmd_dump_after_multi_load(mock_stdout):
# def test_cmd_dump_after_multi_load():
    # with open('tt.json', 'w') as f:
    #     f.write(cp.result)
    # assert False is True
    assert tty_i.dump() is True
    assert json.loads(mock_stdout.getvalue()) == json.loads(fifth_fixture)


@patch('sys.stdout', new_callable=StringIO)
def test_cmd_searchlinks_allresult(mock_stdout):
# def test_cmd_searchlinks_allresult():
    assert tty_i.searchlinks() is True
    assert mock_stdout.getvalue() == ''.join([
        _('%s links totally founded') % '4', ' : \n',
        ' ' * INDENT, 'http://ubuntu.com\n',
        ' ' * INDENT, 'http://linuxfr.org\n',
        ' ' * INDENT, 'http://phoronix.com\n',
        ' ' * INDENT, 'http://xkcd.com\n'
    ])


@patch('sys.stdout', new_callable=StringIO)
def test_cmd_searchlinks_noresult(mock_stdout):
    assert tty_i.searchlinks(['nothing']) is False
    assert mock_stdout.getvalue() == _('No links founded') + '. \n'


@patch('sys.stdout', new_callable=StringIO)
def test_cmd_searchlinks(mock_stdout):
    assert tty_i.searchlinks(['bsd']) is True
    assert mock_stdout.getvalue() == ''.join([
        _('%s links founded') % '2', ' : \n',
        ' ' * INDENT, 'http://linuxfr.org\n',
        ' ' * INDENT, 'http://xkcd.com\n'
    ])
