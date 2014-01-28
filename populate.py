#!/usr/bin/env python
#coding=utf-8
from __future__ import unicode_literals

from linkmanager.db import DataBase

fixture = """{
    "http://sametmax.com": {
        "tags": ["python", "django"],
        "priority": 10,
        "description": "site de sam et max",
        "init date": "2014-01-27T17:37:19.985742+00:00",
        "update date": null
    },
    "http://linuxfr.org": {
        "tags": ["unix", "django"],
        "priority": 8,
        "description": "le repère des barbus",
        "init date": "2014-01-27T17:45:19.985742+00:00",
        "update date": "2014-01-27T17:55:19.985742+00:00"
    },
    "http://lavachelibre.com": {
        "tags": ["unix", "libre"],
        "priority": 5,
        "description": "liste de softs",
        "init date": "2014-01-27T17:57:19.985742+00:00",
        "update date": null
    }
}
"""

DataBase().load(fixture)
print('Database completely loaded.')
