#!/usr/bin/env python
from __future__ import unicode_literals

import codecs
import os
import sys


class CommandError(Exception):
    pass


def find_command(cmd, path=None, pathext=None):
    if path is None:
        path = os.environ.get('PATH', []).split(os.pathsep)
    if isinstance(path, str):
        path = [path]
    # check if there are funny path extensions for executables, e.g. Windows
    if pathext is None:
        pathext = os.environ.get(
            'PATHEXT', '.COM;.EXE;.BAT;.CMD'
        ).split(os.pathsep)
    # don't use extensions if the command ends with one of them
    for ext in pathext:
        if cmd.endswith(ext):
            pathext = ['']
            break
    # check if we find the command on PATH
    for p in path:
        f = os.path.join(p, cmd)
        if os.path.isfile(f):
            return f
        for ext in pathext:
            fext = f + ext
            if os.path.isfile(fext):
                return fext
    return None


def has_bom(fn):
    with open(fn, 'rb') as f:
        sample = f.read(4)
    return sample[:3] == b'\xef\xbb\xbf' or \
        sample.startswith(codecs.BOM_UTF16_LE) or \
        sample.startswith(codecs.BOM_UTF16_BE)


def compile_messages(stderr, locale=None):
    basedirs = [os.path.join('linkmanager', 'locale'), 'locale']
    if os.environ.get('DJANGO_SETTINGS_MODULE'):
        from django.conf import settings
        basedirs.extend(settings.LOCALE_PATHS)

    # Gather existing directories.
    basedirs = set(map(os.path.abspath, filter(os.path.isdir, basedirs)))

    if not basedirs:
        raise CommandError(
            "This script should be run from the LinkManager Git checkout or your project or app tree, or with the settings module specified.")

    for basedir in basedirs:
        if locale:
            basedir = os.path.join(basedir, locale, 'LC_MESSAGES')
        for dirpath, dirnames, filenames in os.walk(basedir):
            for f in filenames:
                if f.endswith('.po'):
                    stderr.write('processing file %s in %s\n' % (f, dirpath))
                    fn = os.path.join(dirpath, f)
                    if has_bom(fn):
                        raise CommandError("The %s file has a BOM (Byte Order Mark). LinkManager only supports .po files encoded in UTF-8 and without any BOM." % fn)
                    pf = os.path.splitext(fn)[0]
                    # Store the names of the .mo and .po files in an environment
                    # variable, rather than doing a string replacement into the
                    # command, so that we can take advantage of shell quoting, to
                    # quote any malicious characters/escaping.
                    # See http://cyberelk.net/tim/articles/cmdline/ar01s02.html
                    os.environ['lmcompilemo'] = pf + '.mo'
                    os.environ['lmcompilepo'] = pf + '.po'
                    if sys.platform == 'win32':
                        cmd = 'msgfmt --check-format -o "%lmcompilemo%" "%lmcompilepo%"'
                    else:
                        cmd = 'msgfmt --check-format -o "$lmcompilemo" "$lmcompilepo"'
                    os.system(cmd)

if __name__ == "__main__":
    #locale = options.get('locale')
    compile_messages(sys.stdout, locale=None)
