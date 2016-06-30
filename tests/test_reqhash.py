#!/usr/bin/env python
"""Unittests for reqhash
"""
import pytest
import reqhash
import six
import subprocess

TO_STR_INPUT = [
    (b'asdf', 'asdf'),
    (u'asdf', u'asdf'),
]
TO_STR_IDS = ["binary", "unicode"]
if six.PY3:
    TO_STR_INPUT.append((u'Hello, \U0001F4A9!'.encode('utf-8'), u'Hello, \U0001F4A9!'))
    TO_STR_IDS.append("poo")


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


@pytest.mark.parametrize("to_str_input", TO_STR_INPUT, ids=TO_STR_IDS)
def test_to_str(to_str_input):
    val = reqhash.to_str(to_str_input[0])
    assert val == to_str_input[1]
