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


Usage
=====

::

    python manage.py detect_cyclic | dot -T svg -o my_imports.svg