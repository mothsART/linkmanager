
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


                                LinkManager 0.1

    _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
    *_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_
     * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *

===========
LinkManager
===========

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
============

Linkmanager depends on **redis** Database.
You must install it like this (on debian/ubuntu) :
    $ sudo apt-get install redis-server

To enjoy completion, you should put that line in your ~/.bashrc (or ~/.zshrc) :
    $ eval "$(register-python-argcomplete linkm)"

Examples
========

    $ linkm add http://stackoverflow.com # add a link on Database
    $ linkm update http://stackoverflow.com # update properties on a existent link
    $ linkm remove http://stackoverflow.com # remove a link on DataBase
    $ linkm search python linux # search a link a link on DataBase with tags
    $ linkm dump >| backup.json # serialize a entire Database on a JSON file
    $ linkm load backup.json # load a list of links on DataBase
    $ linkm flush # erase all DataBase
