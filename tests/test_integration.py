#!/usr/bin/env python
"""Integration tests for reqhash
"""
import os
import pytest
import reqhash
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
        mocker.patch.object(sys, 'argv', new=["reqhash", "-o", tmppath,  req_path])
        with pytest.raises(SystemExit):
            reqhash.cli()
        output = read_file(tmppath)
        assert output == read_file(req_path)
    finally:
        os.remove(tmppath)
