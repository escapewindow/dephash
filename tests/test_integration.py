#!/usr/bin/env python
"""Integration tests for dephash
"""
import logging
import os
import pytest
import random
import dephash
import string
import sys
import tempfile

from . import DATA_DIR, read_file

SKIP_REASON = "NO_TESTS_OVER_WIRE: skipping integration test"

# params {{{1
# Run integration tests against the already pinned+hashed requirements files,
# so we know what versions + hashes to expect.
INTEGRATION_PARAMS = [
    os.path.join(DATA_DIR, "prod1.txt"),
]
if sys.version_info >= (3, 5):
    INTEGRATION_PARAMS.append(os.path.join(DATA_DIR, "prod2.txt"))


# integration tests against test prod.txt reqfiles {{{1
@pytest.mark.skipif(os.environ.get("NO_TESTS_OVER_WIRE"), reason=SKIP_REASON)
@pytest.mark.parametrize("req_path", INTEGRATION_PARAMS)
def test_integration(req_path, mocker):
    try:
        _, tmppath = tempfile.mkstemp()
        mocker.patch.object(sys, 'argv', new=["dephash", "gen", "-o", tmppath, req_path])
        with pytest.raises(SystemExit):
            dephash.gen()
        output = read_file(tmppath)
        assert output == read_file(req_path)
    finally:
        os.remove(tmppath)


@pytest.mark.skipif(os.environ.get("NO_TESTS_OVER_WIRE"), reason=SKIP_REASON)
@pytest.mark.parametrize("req_path", INTEGRATION_PARAMS)
def test_integration_cmdln(req_path, mocker):
    logger = logging.getLogger(
        ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits)
                for _ in range(6))
    )
    mocker.patch.object(dephash, 'log', new=logger)
    try:
        _, logfile = tempfile.mkstemp()
        _, output_file = tempfile.mkstemp()
        mocker.patch.object(sys, 'argv', new=["dephash", "gen", "-v", "-l", logfile, req_path])
        with open(output_file, "w") as fh:
            mocker.patch.object(sys, 'stdout', new=fh)
            with pytest.raises(SystemExit):
                dephash.main()
        output = read_file(output_file)
        assert output == read_file(req_path)
    finally:
        os.remove(output_file)
        os.remove(logfile)
