=======
adjunct
=======

*adjunct* is a collection of miscellaneous modules.

It's intended that this will eventually end up as a namespace package.

Development and Testing
=======================

You should make sure you've `just <https://just.systems/>`_ installed, as it's
used for running maintenance tasks

You're expected to make sure you've `uv <https://docs.astral.sh/uv/>`_
installed as it's used for managing the project. Also, for linting and code
fixes, make sure you've `ruff <https://docs.astral.sh/ruff/>`_ installed too.
If you've *uv* installed already, install *ruff* with::

    uv tool install ruff

For normal development, you can run the test suite with::

    just tests

If you want to run the test suite across all supported Python runtimes, you'll
need `tox <https://tox.wiki/en/4.32.0/>`_. Like with *ruff*, you can install
it with *uv*. You'll need to make sure that you have the *tox-uv* plugin
installed too::

    uv tool install tox --with tox-uv

.. vim:set ft=rst:
