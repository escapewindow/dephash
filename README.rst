===============================
reqhash
===============================

.. image:: https://travis-ci.org/escapewindow/reqhash.svg?branch=master
    :target: https://travis-ci.org/escapewindow/reqhash

.. image:: https://coveralls.io/repos/github/escapewindow/reqhash/badge.svg?branch=master
    :target: https://coveralls.io/github/escapewindow/reqhash?branch=master


Production installs sometimes call for pinning package versions; hash checking adds to the security and stability of those installs.  ``pip >= 8.0.0`` allows for checking package hashes through requirements files.  However, it's easy for requirements to fall out of date, and it's a hassle to test other versions of packages.

With ``reqhash``, a permissive ``requirements-dev.txt`` can be transformed into a fully version-pinned, hashed ``requirements-prod.txt``.

-------
Usage
-------

    reqhash requirements-dev.txt > requirements-prod.txt
