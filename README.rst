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
 * pysmell
 * `pyplete <https://github.com/goinnn/Kate-plugins/blob/master/kate_plugins/pyte_plugins/autocomplete/pyplete.py/>`_


Recomendations
==============
It is possible that the next links are interested if you can some problem:

 * http://code.google.com/p/python-graph/issues/detail?id=15
 * http://stackoverflow.com/questions/2133767/using-python-graphviz-importerror-no-module-named-gv

It is possible that you have to remove the pyc files:

::

    find -iname "*.pyc" -exec rm "{}" \;

Usage
=====

::

    python manage.py detect_cyclic
    python manage.py detect_cyclic --include-apps="app1,app6,app7,app11" --file-name="my_graph.svg" --exclude-packages="migrations,templatetags" --verbosity=2