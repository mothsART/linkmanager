# -*- coding: utf-8 -*-

__appname__ = 'linkmanager'
__author__ = "Jérémie Ferry <jerem.ferry@gmail.com>"
__licence__ = "BSD"
__website__ = "https://github.com/mothsART/linkmanager"
__version__ = '0.4.0.9'
VERSION = tuple(map(int, __version__.split('.')))


def interface(test=False):
    from .tty import TTYInterface
    return TTYInterface(test=test)
