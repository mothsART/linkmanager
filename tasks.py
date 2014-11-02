import gzip

import arrow
from clint.textui.colored import white, green
from invoke import run, task

import linkmanager


# @task
# def clean():
#   run('git clean -Xfd')


@task
def test(f=False, v=False):
    if f:
        run('flake8 *.py **/**.py  --exclude=build/* --exit-zero')
    verbose = ''
    if v:
        verbose = ' -vv'
    run('py.test%s -s linkmanager/tests/tests.py --cov=linkmanager --cov-report term-missing' % verbose, pty=True)  # noqa
    #run('py.test%s -s linkmanager/tests/tests.py --cov=linkmanager --cov-report term-missing --capture=sys' % verbose, pty=True)  # noqa


@task
def trans(pull=False):
    # Future Transifex usage (pip install transifex-client)
    # need python < 3
    # if pull:
    #     run('tx pull -a')
    run('./makemessages.py', pty=True)
    run('./compilemessages.py', pty=True)


@task
def docs():
    run('cd docs; make html; cd ..', pty=True)


def replace(file_path, line_nb, new_line):
    with open(file_path, 'r') as file:
        data = file.readlines()
    if line_nb == -1:
        data = [new_line] + data
    else:
        data[line_nb] = new_line

    with open(file_path, 'w') as file:
        file.writelines(data)


@task
def version(e=None):
    # Read linkmanager version
    if not e:
        print(linkmanager.__version__)
        exit(0)
    e = str(e)
    print('Older version => %s' % e)
    # Edit linkmanager version
    # Edit Manpage
    presentation = '.TH LINKMANAGER 1 "%s" "linkmanager %s"\n' % (
        str(arrow.now())[:10],
        e
    )
    replace(
        'docs/linkmanager.1', 9,
        presentation
    )
    man = open('docs/linkmanager.1', 'rb').read()
    with gzip.open('docs/linkmanager.1.gz', 'wb') as f:
        f.write(man)
    with gzip.open('docs/linkm.1.gz', 'wb') as f:
        f.write(man)

    # Change README version
    replace(
        'README.rst', 27,
        '                                LinkManager %s\n' % e
    )
    # change python version
    replace(
        'linkmanager/__init__.py', 6,
        "__version__ = '{version}'\n".format(version=e)
    )
    # Edit list of changes
    print(
        white('Edit list of changes (finish with "', bg_color='green')
        + white('EOF', bold=True, bg_color='green')
        + white('")', bg_color='green')
    )
    i = 0
    changelog = False
    changes = []
    while True:
        i += 1
        change = input(green('line %s : ' % i))
        if change == 'EOF':
            if i > 1:
                changelog = True
            break
        changes.append(change)
    # # add changelog to HISTORY
    if changelog:
        replace(
            'HISTORY.rst', 2,
            '\n{version} ({date})\n{underline}\n\n{changes}'.format(
                version=e,
                date=str(arrow.now())[:10],
                # 1 space + 2 parenthesis + date length = 13 + version length
                underline=(13 + len(e)) * '-',
                changes=' - ' + '\n- '.join(changes) + '\n\n'
            )
        )
    # add a Debian Changelog
    r = run('date -R', hide='stdout')
    line = ''.join([
        'linkmanager ({version}) saucy;  urgency=low\n'.format(version=e),
        '\n  * ' + '\n  * '.join(changes) + '\n\n',
        ' -- {author} {date}\n'.format(
            author=linkmanager.__author__,
            date=r.stdout
        )
    ])
    if changelog:
        replace(
            'debian/changelog', -1, line
        )
