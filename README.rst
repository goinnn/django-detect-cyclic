====================
Django detect cyclic
====================

Application to detect cyclic imports.
With this application you can analyze the dependence of your applications

Requeriments
============

 * `python-graph-core <http://pypi.python.org/pypi/python-graph-core/>`_ (1.8.1)
 * `python-graph-dot <http://pypi.python.org/pypi/python-graph-dot/>`_ (1.8.1)
 * `pysmell <http://pypi.python.org/pypi/pysmell/>`_ (0.7.3)
 * `pyplete <http://pypi.python.org/pypi/pyplete/>`_ (0.0.1)


Installation
============

In your settings.py:

::

    INSTALLED_APPS = (

        'django_detect_cyclic',

    )


Possibles Errors
================

It is possible that the next links are interested if you can some problem:

 * http://code.google.com/p/python-graph/issues/detail?id=15
 * http://stackoverflow.com/questions/2133767/using-python-graphviz-importerror-no-module-named-gv

It is possible that you have to remove the pyc files:

::

    find -iname "*.pyc" -exec rm "{}" \;

Usage (Examples)
================

::

    python manage.py detect_cyclic
    python manage.py detect_cyclic --include-apps="app1,app6,app7,app11" --file-name="my_graph.svg" --exclude-packages="migrations,templatetags" --verbosity=2
    python manage.py detect_cyclic --include-apps="app1,app6" --show-modules --file-name="my_graph.svg" --exclude-packages="migrations" --verbosity=2
    python manage.py detect_cyclic --include-apps="app1,app6" --only-cyclic --file-name="my_graph.svg" --exclude-packages="migrations" --verbosity=2
