===============================
reqhash
===============================

Production installs sometimes call for pinning package versions; hash checking adds to the security and stability of those installs.  ``pip >= 8.0.0`` allows for checking package hashes through requirements files.  However, it's easy for requirements to fall out of date, and it's a hassle to test other versions of packages.

With ``reqhash``, a permissive ``requirements-dev.txt`` can be transformed into a fully version-pinned, hashed ``requirements-prod.txt``.

-------
Usage
-------

    reqhash requirements-dev.txt

(By default, the output file will replace ``-dev`` with ``-prod`` in the filename, if applicable. If not, the output file will be named ``reqhash.txt``.)

.. important::
    There may be multiple python files for any given module/version, especially between python2 and python3, or source vs. wheel.  This script only gives you one hash per module.  You can deal with this via separate files, e.g. ``requirements-py2-prod.txt``, or by combining various runs together, and specifying multiple ``--hash`` args per module.
