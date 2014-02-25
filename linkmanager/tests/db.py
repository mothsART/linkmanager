import json
from collections import OrderedDict
from unittest.mock import patch

from linkmanager import db as test_db

uuids = [
    'f252f3d1-dfcc-4987-a0c0-3ec057de707a',
    '4c280fe3-2091-4c8d-92fd-660087dd8def',
    '12a10826-9ccc-4123-8f6c-36fb55cbb40e',
]
i_uuids = iter(uuids)


def gen_uuid():
    return next(i_uuids)


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


r = test_db.RedisDb(test=True)
r.flush()


def test_load_redis():
    assert r.load(first_fixture) is True
    assert json.loads(first_fixture) == json.loads(r.dump())


def test_link_exist_redis():
    assert r.link_exist("http://ubuntu.com") is True
    assert r.link_exist("http://42.com") is False


def test_get_link_properties_redis():
    assert r.get_link_properties("http://ubuntu.com") == (
        ['linux', 'python', 'shell', 'ubuntu'],
        '10',
        'Fr Ubuntu site',
        '2014-01-27T17:37:19.985742+00:00'
    )


@patch('uuid.uuid4', gen_uuid)
def test_no_result_redis():
    # All results
    r.flush()
    r.load(first_fixture)
    # No result
    assert r.get_links('linux', 'shell', 'bsd') == []


def test_one_result_redis():
    # One result with multi-tags
    links = [x.decode() for x in r.get_links('linux', 'shell')]
    is_in_uuid = links[0] in uuids
    assert is_in_uuid is True
    # One result with one tag
    links = [x.decode() for x in r.get_links('shell')]
    is_in_uuid = links[0] in uuids
    assert is_in_uuid is True


def test_all_results_redis():
    assert set(r.get_links()) == set([
        '12a10826-9ccc-4123-8f6c-36fb55cbb40e',
        'f252f3d1-dfcc-4987-a0c0-3ec057de707a',
        '4c280fe3-2091-4c8d-92fd-660087dd8def'
    ])


json_addlink = """{
    "http://xkcd.com": {
        "tags": ["joke", "math", "linux", "bsd"],
        "priority": 5,
        "description": "A webcomic of romance ...",
        "init date": "2014-02-06T17:37:19.985742+00:00",
        "update date": null
    }
}
"""


second_fixture = """{
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


def test_addlink_redis():
    assert r.add_link(json_addlink) is True
    assert json.loads(second_fixture) == json.loads(r.dump())


third_fixture = """{
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


def test_deletelink_redis():
    assert r.delete_link("http://linuxfr.org") is True
    assert json.loads(third_fixture) == json.loads(r.dump())


json_updatelink = """{
    "http://xkcd.com": {
        "tags": ["joke", "math", "comic"],
        "priority": 2,
        "description": "A webcomic of ...",
        "init date": "2012-02-06T17:37:19.985742+00:00",
        "update date": "2014-02-07T17:37:19.985742+00:00"
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
    },
    "http://xkcd.com": {
        "description": "A webcomic of ...",
        "init date": "2012-02-06T17:37:19.985742+00:00",
        "priority": "2",
        "tags": [
            "comic",
            "joke",
            "math"
        ],
        "update date": "2014-02-07T17:37:19.985742+00:00"
    }
}
"""


def test_updatelink_redis():
    assert r.update_link(json_updatelink) is True
    assert json.loads(fourth_fixture) == json.loads(r.dump())


def test_sorted_links_redis():
    # One link
    assert r.sorted_links('shell') == OrderedDict([('http://ubuntu.com', 10)])
    # Two links sorted
    assert r.sorted_links('linux') == OrderedDict([
        ('http://ubuntu.com', 10),
        ('http://phoronix.com', 5)
    ])
    # All links sorted
    assert r.sorted_links() == OrderedDict([
        ('http://ubuntu.com', 10),
        ('http://phoronix.com', 5),
        ('http://xkcd.com', 2)
    ])
    # Sorted and give properties
    r.properties = True
    assert r.sorted_links() == OrderedDict([
        (
            'http://ubuntu.com',
            {
                b'init date': b'2014-01-27T17:37:19.985742+00:00',
                b'priority': b'10',
                b'description': b'Fr Ubuntu site',
                b'name': b'http://ubuntu.com',
                b'update date': b'None'
            }
        ),
        (
            'http://phoronix.com',
            {
                b'init date': b'2014-01-27T17:57:19.985742+00:00',
                b'priority': b'5',
                b'description': b'OS benchmarkin',
                b'name': b'http://phoronix.com',
                b'update date': b'None'
            }
        ),
        (
            'http://xkcd.com',
            {
                b'init date': b'2012-02-06T17:37:19.985742+00:00',
                b'priority': b'2',
                b'description': b'A webcomic of ...',
                b'name': b'http://xkcd.com',
                b'update date': b'2014-02-07T17:37:19.985742+00:00'
            }
        )
    ])
