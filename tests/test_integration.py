#!/usr/bin/env python
"""Integration tests for reqhash
"""
import os
import pytest
import reqhash
import sys

from . import DATA_DIR, read_file

SKIP_REASON = "NO_TESTS_OVER_WIRE: skipping integration test"
OUTFILE = os.path.join(DATA_DIR, "reqhash.out")

# params {{{1
# Run integration tests against the already pinned+hashed requirements files,
# so we know what versions + hashes to expect.
INTEGRATION_PARAMS = [
    os.path.join(DATA_DIR, "prod1.txt"),
]
if sys.version_info >= (3, 5):
    INTEGRATION_PARAMS.append(os.path.join(DATA_DIR, "prod2.txt"))
BAD_ARGS_PARAMS = [
    ("reqhash", "one", "two"),
    ("reqhash", ),
]


# helper functions {{{1
def cleanup():
    if os.path.exists(OUTFILE):
        os.remove(OUTFILE)


# integration tests against test prod.txt reqfiles {{{1
@pytest.mark.skipif(os.environ.get("NO_TESTS_OVER_WIRE"), reason=SKIP_REASON)
@pytest.mark.parametrize("req_path", INTEGRATION_PARAMS)
def test_integration(req_path, mocker):
    cleanup()
    mocker.patch.object(sys, 'argv', new=["reqhash", req_path])
    try:
        reqhash.main()
        output = read_file(os.path.join(OUTFILE))
        assert output == read_file(req_path)
    finally:
        cleanup()


# Test that main() dies if passed a bad num of args
# This is here because it could result in running all of main() if the test
# fails
@pytest.mark.skipif(os.environ.get("NO_TESTS_OVER_WIRE"), reason=SKIP_REASON)
@pytest.mark.parametrize("args", BAD_ARGS_PARAMS)
def test_bad_args(args, mocker):
    mocker.patch.object(sys, 'argv', new=args)
    with pytest.raises(SystemExit):
        reqhash.main()
