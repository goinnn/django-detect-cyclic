====================
Django detect cyclic
====================

Examples
========

In these examples we propose a typical sequence to find the cycles in our project, and can see dangerous dependencies


Call to the command without options (only verbosity, and exclude the south migrations):

::

    ./bin/django detect_cyclic --file-name="examples/example-first.svg" --verbosity=2 --exclude-packages=migrations
    ./bin/django detect_cyclic --file-name="examples/example-first.png" --verbosity=2 --exclude-packages=migrations
    INFO: Duration: 0:00:06.611381

.. image:: https://github.com/goinnn/django-detect-cyclic/raw/master/examples/example-first.png

In this image I can not see anything. I am interested in the cycles, I use this options (only-cyclic).:

::

    ./bin/django detect_cyclic --file-name="examples/example-only-cyclic.svg" --verbosity=2 --only-cyclic --exclude-packages=migrations
    ./bin/django detect_cyclic --file-name="examples/example-only-cyclic.png" --verbosity=2 --only-cyclic --exclude-packages=migrations
    INFO: Duration: 0:00:06.535613

.. image:: https://github.com/goinnn/django-detect-cyclic/raw/master/examples/example-only-cyclic.png

I exclude the django applications (exclude-apps):

::

    ./bin/django detect_cyclic --file-name="examples/example-only-cyclic-exclude.svg" --exclude-apps="django.contrib.messages,django.contrib.auth,django.contrib.contenttypes,django.contrib.admin" --verbosity=2 --only-cyclic --exclude-packages=migrations
    ./bin/django detect_cyclic --file-name="examples/example-only-cyclic-exclude.png" --exclude-apps="django.contrib.messages,django.contrib.auth,django.contrib.contenttypes,django.contrib.admin" --verbosity=2 --only-cyclic --exclude-packages=migrations
    INFO: Duration: 0:00:05.038461

.. image:: https://github.com/goinnn/django-detect-cyclic/raw/master/examples/example-only-cyclic-exclude.png

I want to analize the cycles. I need to know modules which are involved in these cycles. Now the nodes are the modules, before the nodes were the applications:

::

    ./bin/django detect_cyclic --file-name="examples/example-modules.svg" --verbosity=2 --only-cyclic --include-apps=bpmui,authentication,wfui,cmisadaptor,wfadaptor --show-modules --exclude-packages=migrations
    ./bin/django detect_cyclic --file-name="examples/example-modules.png" --verbosity=2 --only-cyclic --include-apps=bpmui,authentication,wfui,cmisadaptor,wfadaptor --show-modules --exclude-packages=migrations
    INFO: Duration: 0:00:27.532323

.. image:: https://github.com/goinnn/django-detect-cyclic/raw/master/examples/example-modules.png


Also I want to know what import is into a function and what import is a global import (dotted-scope-local):

::

    ./bin/django detect_cyclic --file-name="examples/example-modules-dotted.svg" --verbosity=0 --only-cyclic --include-apps=bpmui,authentication,wfui,cmisadaptor,wfadaptor --show-modules --exclude-packages=migrations --dotted-scope-local
    ./bin/django detect_cyclic --file-name="examples/example-modules-dotted.png" --verbosity=0 --only-cyclic --include-apps=bpmui,authentication,wfui,cmisadaptor,wfadaptor --show-modules --exclude-packages=migrations --dotted-scope-local
    INFO: Duration: 0:00:34.074046

.. image:: https://github.com/goinnn/django-detect-cyclic/raw/master/examples/example-modules-dotted.png


Now you can to do the same from admin site:

.. image:: https://github.com/goinnn/django-detect-cyclic/raw/master/examples/wizard.png

There is a special format only from the wizard. This is "svg-js". The graph is rendered with `dracula <http://www.graphdracula.net/>`_

.. image:: https://github.com/goinnn/django-detect-cyclic/raw/master/examples/wizard-svg-js.png

We can use other options, instead of only-cyclic we could use remove-isolate-nodes, remove-source-nodes or remove-sink-nodes to limit the graph.
We can use scope-global to see only the global imports.

::

    Options:
        -v VERBOSITY, --verbosity=VERBOSITY
                                Verbosity level; 0=minimal output, 1=normal output,
                                2=all output
        --settings=SETTINGS   The Python path to a settings module, e.g.
                                "myproject.settings.main". If this isn't provided, the
                                DJANGO_SETTINGS_MODULE environment variable will be
                                used.
        --pythonpath=PYTHONPATH
                                A directory to add to the Python path, e.g.
                                "/home/djangoprojects/myproject".
        --traceback           Print traceback on exception
        -i INCLUDE_APPS, --include-apps=INCLUDE_APPS
                                Only use these applications to the graph (separated by
                                commas)
        -e EXCLUDE_APPS, --exclude-apps=EXCLUDE_APPS
                                Exclude these apps to the graph (separated by commas)
        -f FILE_NAME, --file-name=FILE_NAME
                                The name to the generated path (you can set with path)
        -p EXCLUDE_PACKAGES, --exclude-packages=EXCLUDE_PACKAGES
                                Exclude the next packages. For example
                                migrations,templatetags (separated by commas)
        -c, --force-colors    You can use this option when the format are not svg
        -g, --scope-global    The imports into the functions are ignored
        -d, --dotted-scope-local
                                The imports into the functions are printing with
                                dotted line
        -s, --show-modules    The nodes now are the modules (by default are the
                                applications)
        -o, --only-cyclic     Removes the nodes that do not belong to any cycle
        -r, --remove-isolate-nodes
                                Removes the isolate nodes
        -k, --remove-sink-nodes
                                Removes the sink nodes
        -a, --remove-source-nodes
                                Removes the source nodes
        -l LAYOUT, --layout=LAYOUT
                                Removes the source nodes
        --version             show program's version number and exit
        -h, --help            show this help message and exit
