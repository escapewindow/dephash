#!/usr/bin/env python

import pytest
import reqhash
import subprocess


def test_die():
    with pytest.raises(SystemExit):
        reqhash.die("foo")


def test_usage():
    with pytest.raises(SystemExit):
        reqhash.usage()


def test_run_cmd_success():
    val = reqhash.run_cmd("echo")
    assert val == 0


def test_run_cmd_failure():
    with pytest.raises(subprocess.CalledProcessError):
        reqhash.run_cmd(['bash', '-c', 'exit 1'])
