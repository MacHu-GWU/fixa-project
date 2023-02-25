
.. image:: https://readthedocs.org/projects/fixa/badge/?version=latest
    :target: https://fixa.readthedocs.io/index.html
    :alt: Documentation Status

.. image:: https://github.com/MacHu-GWU/fixa-project/workflows/CI/badge.svg
    :target: https://github.com/MacHu-GWU/fixa-project/actions?query=workflow:CI

.. image:: https://codecov.io/gh/MacHu-GWU/fixa-project/branch/main/graph/badge.svg
    :target: https://codecov.io/gh/MacHu-GWU/fixa-project

.. image:: https://img.shields.io/pypi/v/fixa.svg
    :target: https://pypi.python.org/pypi/fixa

.. image:: https://img.shields.io/pypi/l/fixa.svg
    :target: https://pypi.python.org/pypi/fixa

.. image:: https://img.shields.io/pypi/pyversions/fixa.svg
    :target: https://pypi.python.org/pypi/fixa

.. image:: https://img.shields.io/badge/STAR_Me_on_GitHub!--None.svg?style=social
    :target: https://github.com/MacHu-GWU/fixa-project

------


.. image:: https://img.shields.io/badge/Link-Document-blue.svg
    :target: https://fixa.readthedocs.io/index.html

.. image:: https://img.shields.io/badge/Link-API-blue.svg
    :target: https://fixa.readthedocs.io/py-modindex.html

.. image:: https://img.shields.io/badge/Link-Source_Code-blue.svg
    :target: https://fixa.readthedocs.io/py-modindex.html

.. image:: https://img.shields.io/badge/Link-Install-blue.svg
    :target: `install`_

.. image:: https://img.shields.io/badge/Link-GitHub-blue.svg
    :target: https://github.com/MacHu-GWU/fixa-project

.. image:: https://img.shields.io/badge/Link-Submit_Issue-blue.svg
    :target: https://github.com/MacHu-GWU/fixa-project/issues

.. image:: https://img.shields.io/badge/Link-Request_Feature-blue.svg
    :target: https://github.com/MacHu-GWU/fixa-project/issues

.. image:: https://img.shields.io/badge/Link-Download-blue.svg
    :target: https://pypi.org/pypi/fixa#files


Welcome to ``fixa`` Documentation
==============================================================================
Like the `Ikea FIXA <https://www.ikea.com/us/en/p/fixa-17-piece-tool-kit-00169254/>`_, it is my Python toolbox for small projects.

This library is inspired by `boltons <https://boltons.readthedocs.io/en/latest/>`_.

Integration options:

Utility libraries are often used extensively within a project, and because they are not often fundamental to the architecture of the application, simplicity and stability may take precedence over version recency. In these cases, developers can:

- Copy the whole fix package into a project.
- Copy just the ``***.py`` file that a project requires.

Modules and Examples:

- `hashes <./examples/hashes.ipynb>`_
- `nested_logger <./examples/nested_logger.ipynb>`_
- `timer <./examples/timer.ipynb>`_


.. _install:

Install
------------------------------------------------------------------------------

``fixa`` is released on PyPI, so all you need is:

.. code-block:: console

    $ pip install fixa

To upgrade to latest version:

.. code-block:: console

    $ pip install --upgrade fixa
