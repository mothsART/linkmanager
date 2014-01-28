#!/usr/bin/env python

import fnmatch
import re
import glob
import os
import sys
from itertools import dropwhile
from subprocess import (Popen, PIPE)

STATUS_OK = 0


class CommandError(Exception):
    pass


def is_ignored(path, ignore_patterns):
    """
    Helper function to check if the given path should be ignored or not.
    """
    for pattern in ignore_patterns:
        if fnmatch.fnmatchcase(path, pattern):
            return True
    return False


# def copy_plural_forms(msgs, locale, domain, verbosity, stdout=sys.stdout):
#     """
#     Copies plural forms header contents from a Django catalog of locale to
#     the msgs string, inserting it at the right place. msgs should be the
#     contents of a newly created .po file.
#     """
#     django_dir = os.path.normpath(os.path.join(os.path.dirname(django.__file__)))
#     if domain == 'djangojs':
#         domains = ('djangojs', 'django')
#     else:
#         domains = ('django',)
#     for domain in domains:
#         django_po = os.path.join(django_dir, 'conf', 'locale', locale, 'LC_MESSAGES', '%s.po' % domain)
#         if os.path.exists(django_po):
#             with open(django_po, 'rU') as fp:
#                 m = plural_forms_re.search(fp.read())
#             if m:
#                 if verbosity > 1:
#                     stdout.write("copying plural forms: %s\n" % m.group('value'))
#                 lines = []
#                 seen = False
#                 for line in msgs.split('\n'):
#                     if not line and not seen:
#                         line = '%s\n' % m.group('value')
#                         seen = True
#                     lines.append(line)
#                 msgs = '\n'.join(lines)
#                 break
#     return msgs


def write_pot_file(potfile, msgs, file, work_file, is_templatized):
    """
    Write the :param potfile: POT file with the :param msgs: contents,
    previously making sure its format is valid.
    """
    if is_templatized:
        old = '#: ' + work_file[2:]
        new = '#: ' + file[2:]
        msgs = msgs.replace(old, new)
    if os.path.exists(potfile):
        # Strip the header
        msgs = '\n'.join(dropwhile(len, msgs.split('\n')))
    else:
        msgs = msgs.replace('charset=CHARSET', 'charset=UTF-8')
    with open(potfile, 'a') as fp:
        fp.write(msgs)


def write_po_file(pofile, potfile, domain, locale, verbosity, stdout,
                  copy_pforms, wrap, location, no_obsolete):
    """
    Creates of updates the :param pofile: PO file for :param domain: and :param
    locale:.  Uses contents of the existing :param potfile:.

    Uses mguniq, msgmerge, and msgattrib GNU gettext utilities.
    """
    msgs, errors, status = _popen('msguniq %s %s --to-code=utf-8 "%s"' %
                                    (wrap, location, potfile))
    if errors:
        if status != STATUS_OK:
            os.unlink(potfile)
            raise CommandError(
                "errors happened while running msguniq\n%s" % errors)
        elif verbosity > 0:
            stdout.write(errors)

    if os.path.exists(pofile):
        with open(potfile, 'w') as fp:
            fp.write(msgs)
        msgs, errors, status = _popen('msgmerge %s %s -q "%s" "%s"' %
                                        (wrap, location, pofile, potfile))
        if errors:
            if status != STATUS_OK:
                os.unlink(potfile)
                raise CommandError(
                    "errors happened while running msgmerge\n%s" % errors)
            elif verbosity > 0:
                stdout.write(errors)
    # elif copy_pforms:
    #     msgs = copy_plural_forms(msgs, locale, domain, verbosity, stdout)
    msgs = msgs.replace(
        "#. #-#-#-#-#  %s.pot (PACKAGE VERSION)  #-#-#-#-#\n" % domain, "")
    with open(pofile, 'w') as fp:
        fp.write(msgs)
    os.unlink(potfile)
    if no_obsolete:
        msgs, errors, status = _popen(
            'msgattrib %s %s -o "%s" --no-obsolete "%s"' %
            (wrap, location, pofile, pofile))
        if errors:
            if status != STATUS_OK:
                raise CommandError(
                    "errors happened while running msgattrib\n%s" % errors)
            elif verbosity > 0:
                stdout.write(errors)


def _popen(cmd):
    """
    Friendly wrapper around Popen for Windows
    """
    p = Popen(
        cmd, shell=True, stdout=PIPE, stderr=PIPE,
        close_fds=os.name != 'nt', universal_newlines=True
    )
    output, errors = p.communicate()
    return output, errors, p.returncode


def find_files(root, ignore_patterns, verbosity, stdout=sys.stdout, symlinks=False):
    """
    Helper function to get all files in the given root.
    """
    dir_suffix = '%s*' % os.sep
    norm_patterns = [p[:-len(dir_suffix)] if p.endswith(dir_suffix) else p for p in ignore_patterns]
    all_files = []
    for dirpath, dirnames, filenames in os.walk(root, topdown=True, followlinks=symlinks):
        for dirname in dirnames[:]:
            if is_ignored(os.path.normpath(os.path.join(dirpath, dirname)), norm_patterns):
                dirnames.remove(dirname)
                if verbosity > 1:
                    stdout.write('ignoring directory %s\n' % dirname)
        for filename in filenames:
            if is_ignored(os.path.normpath(os.path.join(dirpath, filename)), ignore_patterns):
                if verbosity > 1:
                    stdout.write('ignoring file %s in %s\n' % (filename, dirpath))
            else:
                all_files.extend([(dirpath, filename)])
    all_files.sort()
    return all_files

args = [
    'xgettext',
    '-d django',
    '--language=Python',
    '--keyword=gettext_noop',
    '--keyword=gettext_lazy',
    '--keyword=ngettext_lazy:1,2',
    '--keyword=ugettext_noop',
    '--keyword=ugettext_lazy',
    '--keyword=ungettext_lazy:1,2',
    '--keyword=pgettext:1c,2',
    '--keyword=npgettext:1c,2,3',
    '--keyword=pgettext_lazy:1c,2',
    '--keyword=npgettext_lazy:1c,2,3',
    '--from-code=UTF-8',
    '--add-comments=Translators'
]

if __name__ == "__main__":
    verbosity = 1
    stdout = sys.stdout
    is_templatized = False
    wrap = ''
    location = ''
    no_obsolete = False

    # We require gettext version 0.15 or newer.
    output, errors, status = _popen('xgettext --version')
    if status != STATUS_OK:
        raise CommandError(
            "Error running xgettext. Note that Django "
            "internationalization requires GNU gettext 0.15 or newer."
        )
    match = re.search(r'(?P<major>\d+)\.(?P<minor>\d+)', output)
    if match:
        xversion = (int(match.group('major')), int(match.group('minor')))
        if xversion < (0, 15):
            raise CommandError(
                "Linkmanager internationalization requires GNU "
                "gettext 0.15 or newer. You are using version %s, please "
                "upgrade your gettext toolset." % match.group()
            )

    locales = []
    # if locale is not None:
    #     locales.append(str(locale))
    # elif all:
    localedir = os.path.abspath(os.path.join('linkmanager', 'locale'))
    locale_dirs = filter(os.path.isdir, glob.glob('%s/*' % localedir))
    locales = [os.path.basename(l) for l in locale_dirs]

    for locale in locales:
        if verbosity > 0:
            stdout.write("processing language %s\n" % locale)
        basedir = os.path.join(localedir, locale, 'LC_MESSAGES')
        if not os.path.isdir(basedir):
            os.makedirs(basedir)

        pofile = os.path.join(basedir, 'linkmanager.po')
        potfile = os.path.join(basedir, 'linkmanager.pot')

        if os.path.exists(potfile):
            os.unlink(potfile)

        for dirpath, file in find_files(
            ".", ['.*', './.git', 'CVS', '.pyc', '*~'],
            verbosity, stdout, False
        ):
            _, file_ext = os.path.splitext(file)
            if file_ext == '.py':
                orig_file = os.path.join(dirpath, file)
                work_file = orig_file
                # with open(orig_file, "rU") as fp:
                #     src_data = fp.read()
                # thefile = '%s.py' % file
                # #content = templatize(src_data, orig_file[2:])
                # with open(os.path.join(dirpath, thefile), "w") as fp:
                #     #fp.write(content)
                #     fp.write(src_data)

                args.append('-o %s ' % pofile)
                args.append(work_file)

                msgs, errors, status = _popen(' '.join(args))
                if msgs:
                    write_pot_file(potfile, msgs, file, work_file, is_templatized)

        if os.path.exists(potfile):
            write_po_file(
                pofile, potfile, 'linkmanager', locale, verbosity, stdout,
                True, wrap, location, no_obsolete
            )
