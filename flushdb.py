#!/usr/bin/env python

from linkmanager.db import DataBase

DataBase().flush()
print('All keys in the current database was deleted.')
