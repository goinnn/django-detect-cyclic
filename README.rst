.. contents::

====================
Django detect cyclic
====================

Application to detect cyclic imports.
With this application you can analyze the dependence of your applications

.. image:: https://github.com/goinnn/django-detect-cyclic/raw/master/examples/example-only-cyclic-exclude.png

Requeriments
============

 * `python-graph-core <http://pypi.python.org/pypi/python-graph-core/>`_ (1.8.1)
 * `python-graph-dot <http://pypi.python.org/pypi/python-graph-dot/>`_ (1.8.1)
 * `pysmell <http://pypi.python.org/pypi/pysmell/>`_ (0.7.3)
 * `pyplete <http://pypi.python.org/pypi/pyplete/>`_ (0.0.1)
 * `django-form-admin <http://pypi.python.org/pypi/django-form-admin>`_ (0.3.2) (optional)
 * `jquery.graphviz <https://github.com/goinnn/jquery.graphviz/>`_ (fronzen into the app, only to svg-js format)


Installation
============

In your settings.py:

::

    INSTALLED_APPS = (

        'django_detect_cyclic',

    )

In your urls.py:

::

    urlpatterns = patterns('',

        (r'^admin/detect_cyclic/', include('django_detect_cyclic.urls')),

    )

Caption
=======

 * The nodes are applications, or (if you use the option “Show modules”) modules in the applications
 * One edge means that the source node imports from the destination node
 * Every edge of a cycle has the same background color and the label contains “Cycle X”
 * The labels of the edges contain the weight in parentheses
 * If you use the “Show modules” option, each node will have a background color. If two nodes are from the same application, they will have the same background color.
 * If an edge is dotted, every import in the source happens at runtime, whithin the body of a function or method


Possibles Errors
================

It is possible that the next links are interested if you can some problem:

 * http://code.google.com/p/python-graph/issues/detail?id=15
 * http://stackoverflow.com/questions/2133767/using-python-graphviz-importerror-no-module-named-gv

It is possible that you have to remove the pyc files:

::

    find -iname "*.pyc" -exec rm "{}" \;

Usage 
=====

You have two ways, you can run a command:

::

    python manage.py detect_cyclic
    python manage.py detect_cyclic --include-apps="app1,app6,app7,app11" --file-name="my_graph.svg" --exclude-packages="migrations,templatetags" --verbosity=2
    python manage.py detect_cyclic --include-apps="app1,app6" --show-modules --file-name="my_graph.svg" --exclude-packages="migrations" --verbosity=2
    python manage.py detect_cyclic --include-apps="app1,app6" --only-cyclic --file-name="my_graph.svg" --exclude-packages="migrations" --verbosity=2

Or you can access via web to the wizard:

::

   /admin/detect_cyclic/


Examples
========

To see more examples click in `examples <https://github.com/goinnn/django-detect-cyclic/blob/master/EXAMPLES.rst/>`_
