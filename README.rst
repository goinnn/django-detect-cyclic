====================
Django detect cyclic
====================

Application to detect cyclic imports

Installation
============

::

    INSTALLED_APPS = (

        'django_detect_cyclic',

    )


Requeriments
============

 * python-graph-core
 * python-graph-dot

It is possible that the next links are interested if you can some problem:

 * http://code.google.com/p/python-graph/issues/detail?id=15
 * http://stackoverflow.com/questions/2133767/using-python-graphviz-importerror-no-module-named-gv

Usage
=====

::

    python manage.py detect_cyclic