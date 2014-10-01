.. image:: https://badge.fury.io/py/linkmanager.png
    :target: http://badge.fury.io/py/linkmanager

.. image:: https://pypip.in/d/linkmanager/badge.png
    :target: https://pypi.python.org/pypi/linkmanager

.. image:: https://travis-ci.org/mothsART/linkmanager.png?branch=master
   :target: https://travis-ci.org/mothsART/linkmanager

.. image:: https://coveralls.io/repos/mothsART/linkmanager/badge.png?branch=master
    :target: https://coveralls.io/r/mothsART/linkmanager?branch=master

::

    _*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_
    *_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*

           _
          |_|
      _    _ __    _ _   __   __      ___ ___  __    __ ___   ______  ______ ______
     | |  | |  \  | | | / /  |  \    /  |/ _ \|  \  | |/ _ \ /  ____|| _____|  __  \
     | |  | |   \ | | |/ / _ |   \  /   | |_| |   \ | | |_| |  /  ___|  |___| |__| |
     | |  | | |\ \| |   \ |_|| |\ \/ /| |  _  | |\ \| |  _  | |  |_ _|  ___||     _/
     | |__| | | \   | |\ \   | | \  / | | | | | | \   | | | |  \__| ||  |___| |\  \
     |____|_|_|  \__|_| \_\  |_|  \/  |_|_| |_|_|  \__|_| |_|\______/|______|_| \__\


                                LinkManager 0.4.0.9

    _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
    *_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_
     * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *


**LinkManager** manage your link on terminal.

Replace bookmark tool present on browser because :
    * is often heavy
    * dependent of the browser in question
    * has a lot of frills
    * DataBase usage depend on browser
    * find a local link should not require several hundred MB of Ram and eat your CPU
    * one software for one thing (Unix Philosophy)
    * KISS for import/export
    * many other good reasons


Requirements
------------

Linkmanager depends on **redis** Database and GIT (personnal "clint" version).
You must install it like this (on debian/ubuntu) :

.. code-block:: bash

    $ sudo apt-get install redis-server git

To enjoy "completion", you normaly should do nothing.
A "sudo pip install" should add it automatically.
Otherwise, just put that line in your ~/.bashrc (or ~/.zshrc) :

.. code-block:: bash

    $ eval "$(register-python-argcomplete linkm)"


Examples
--------

.. code-block:: bash

    $ linkm add http://stackoverflow.com # add a link on Database
    $ linkm update http://stackoverflow.com # update properties on a existent link
    $ linkm remove http://stackoverflow.com # remove a link on DataBase
    $ linkm search python linux # search a link a link on DataBase with tags
    $ linkm dump >| backup.json # serialize a entire Database on a JSON file
    $ linkm load backup.json # load a list of links on DataBase
    $ linkm flush # erase all DataBase

when you add/edit links, the "shell" will ask you for each one to edit tags, priority value and a description.

.. code-block:: bash

    $ linkm add http://djangoproject.com
        "http://djangoproject.com" properties :
            tags (separate with ",") : django, python, framework
            priority value (integer value between 1 and 10) : 5
            give a description : Django is a high-level Python Web framework that encourages rapid development and clean, pragmatic design.
