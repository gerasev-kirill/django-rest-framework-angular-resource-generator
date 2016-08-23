=====
Angular resource generator for DRF
=====


Detailed documentation is in the "docs" directory.

Quick start
-----------

1. Add "drf_ng_generator" to your INSTALLED_APPS setting like this::

      INSTALLED_APPS = (
          ...
          'drf_ng_generator',
      )

2. Run `python manage.py drf_ng ./path/to/my/newResrource.coffee` to create
the ngResource from drf views.
