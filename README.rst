===============================
dephash
===============================

---------
You probably want `pip-compile <https://pypi.org/project/pip-tools/>`_ or `pip-compile-multi <https://pypi.org/project/pip-compile-multi/>`_. Dephash was `written before pip-tools allowed for pinning with hashes <https://escapewindow.dreamwidth.org/247093.html>`_.
---------

.. image:: https://travis-ci.org/escapewindow/dephash.svg?branch=master
    :target: https://travis-ci.org/escapewindow/dephash

.. image:: https://coveralls.io/repos/github/escapewindow/dephash/badge.svg?branch=master
    :target: https://coveralls.io/github/escapewindow/dephash?branch=master


Production installs sometimes call for pinning package versions; hash checking adds to the security and stability of those installs.  ``pip >= 8.0.0`` allows for checking package hashes through requirements files.  However, it's easy for requirements to fall out of date, and it's a hassle to test other versions of packages.

With ``dephash``, a permissive ``requirements-dev.txt`` can be transformed into a fully version-pinned, hashed ``requirements-prod.txt``.

-------
Usage
-------

.. code-block:: bash

    # Generate pinned+hashed requirements-prod.txt
    dephash [-v] [-l,--logfile LOGFILE] gen requirements-dev.txt > requirements-prod.txt
    
    # Check for outdated packages in PATH, where PATH is a virtualenv or requirements file
    dephash [-v] [-l,--logfile LOGFILE] outdated PATH
