===============================
reqhash
===============================

Production installs sometimes call for pinning package versions; hash checking adds to the security and stability of those installs.  pip >= 8.0.0 allows for checking package hashes through requirements files.  However, it's easy for requirements to fall out of date, and it's a hassle to test other versions of packages.

With ``reqhash``, a permissive ``requirements-dev.txt`` can be transformed into a fully version-pinned, hashed ``requirements-prod.txt``.

(By default, the output file will replace ``-dev`` with ``-prod`` in the filename, if applicable. If not, the output file will be named ``reqhash.txt``.)

Usage:

    reqhash requirements-dev.txt
