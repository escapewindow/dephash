#!/usr/bin/env python
"""Unittests for reqhash
"""
import os
import pytest
import reqhash
import six
import subprocess

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

# params {{{1
TO_STR_PARAMS = [
    (b'asdf', 'asdf'),
    (u'asdf', u'asdf'),
]
TO_STR_IDS = ["binary", "unicode"]
if six.PY3:
    TO_STR_PARAMS.append((u'Hello, \U0001F4A9!'.encode('utf-8'), u'Hello, \U0001F4A9!'))
    TO_STR_IDS.append("poo")

GET_OUTPUT_PARAMS = [
    (["echo", "foo"], "foo"),
    (["bash", "-c", "echo bar && >&2 echo foo"], "bar"),
]
GET_OUTPUT_IDS = ["stdout", "stdout+stderr"]

PIP_FREEZE_PARAMS = [(
    os.path.join(DATA_DIR, "freeze1.txt"),
    {
        "mercurial": {"version": "3.8.3"},
        "pluggy": {"version": "0.3.1"},
        "powerline-status": {"version": "2.4"},
        "py": {"version": "1.4.31"},
        "six": {"version": "1.10.0"},
        "tox": {"version": "2.3.1"},
        "vboxapi": {"version": "1.0"},
        "virtualenv": {"version": "14.0.6"},
    }
), (
    os.path.join(DATA_DIR, "freeze2.txt"),
    {
        "aiohttp": {"version": "0.22.0a0"},
        "arrow": {"version": "0.8.0"},
        "chardet": {"version": "2.3.0"},
        "defusedxml": {"version": "0.4.1"},
        "ecdsa": {"version": "0.13"},
        "flake8": {"version": "2.6.2"},
        "frozendict": {"version": "0.6"},
        "future": {"version": "0.15.2"},
        "jsonschema": {"version": "2.5.1"},
        "mccabe": {"version": "0.5.0"},
        "mohawk": {"version": "0.3.2.1"},
        "multidict": {"version": "1.1.0b4"},
        "pefile": {"version": "2016.3.28"},
        "pycodestyle": {"version": "2.0.0"},
        "pycrypto": {"version": "2.6.1"},
        "pyflakes": {"version": "1.2.3"},
        "python-dateutil": {"version": "2.5.3"},
        "python-jose": {"version": "0.7.0"},
        "requests": {"version": "2.10.0"},
        "signtool": {"version": "1.0.9a0"},
        "six": {"version": "1.10.0"},
        "slugid": {"version": "1.0.7"},
        "taskcluster": {"version": "0.3.4"},
        "virtualenv": {"version": "15.0.2"},
    }
)]


# die, usage {{{1
def test_die():
    with pytest.raises(SystemExit):
        reqhash.die("foo")


def test_usage():
    with pytest.raises(SystemExit):
        reqhash.usage()


# run_cmd {{{1
def test_run_cmd_success():
    val = reqhash.run_cmd("echo")
    assert val == 0


def test_run_cmd_failure():
    with pytest.raises(subprocess.CalledProcessError):
        reqhash.run_cmd(['bash', '-c', 'exit 1'])


# to_str {{{1
@pytest.mark.parametrize("params", TO_STR_PARAMS, ids=TO_STR_IDS)
def test_to_str(params):
    val = reqhash.to_str(params[0])
    assert val == params[1]


# get_output {{{1
@pytest.mark.parametrize("params", GET_OUTPUT_PARAMS, ids=GET_OUTPUT_IDS)
def test_get_output(params):
    output = reqhash.get_output(params[0])
    assert output.rstrip() == params[1]


def test_get_output_error():
    with pytest.raises(subprocess.CalledProcessError):
        reqhash.get_output(["bash", "-c", "echo foo && exit 1"])


# parse_pip_freeze {{{1
@pytest.mark.parametrize("params", PIP_FREEZE_PARAMS)
def test_parse_pip_freeze(params):
    with open(params[0], "r") as fh:
        module_dict = reqhash.parse_pip_freeze(fh.read())
        assert module_dict == params[1]
