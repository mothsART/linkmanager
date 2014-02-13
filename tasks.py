from invoke import run, task


# @task
# def clean():
    #run('git clean -Xfd')


@task
def test(v=False):
    #run('flake8 .')
    verbose = ''
    if v:
        verbose = ' -vv'
    run('py.test%s linkmanager/tests/tests.py --cov=linkmanager --cov-report term-missing' % verbose)


@task
def trans(pull=False):
    ### Future Transifex usage (pip install transifex-client)
    ### need python < 3
    # if pull:
    #     run('tx pull -a')
    run('./makemessages')
    run('./compilemessages')


@task
def docs():
    run('cd docs; make html; cd ..')
