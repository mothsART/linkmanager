#!/usr/bin/env python
#coding=utf-8
from __future__ import unicode_literals

from linkmanager.db import DataBase

links = DataBase().get_links('django')
print(links)

print('=' * 50)

print(DataBase().sort_by_priority(links))

print('=' * 50)

for l in links:
    print(DataBase().get_properties(l))
