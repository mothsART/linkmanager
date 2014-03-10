# encoding=utf8

__appname__ = 'linkmanager'
__author__ = "Ferry Jérémie <jerem.ferry@gmail.com>"
__licence__ = "BSD"
__website__ = "https://github.com/mothsART/linkmanager"
__version__ = '0.1.4'
VERSION = tuple(map(int, __version__.split('.')))


def interface():
    from .tty import TTYInterface # NOQA
    return TTYInterface()
