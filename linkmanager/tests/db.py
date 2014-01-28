import pytest

from linkmanager import db


@pytest.fixture
def links_json():
    links = {
        'tag1': ['link1', 'link3', 'link5'],
        'tag1': ['link3', 'link5', 'link7']
    }
    return links


def test_redis_loadjson(links_json):
    r = db.RedisDb()
    assert r.load(links_json) == True
