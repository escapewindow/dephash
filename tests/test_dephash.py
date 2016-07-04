#!/usr/bin/env python
"""Unittests for dephash
"""
import os
import pytest
import dephash
import six
import subprocess

from . import DATA_DIR, load_json, read_file

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
    os.path.join(DATA_DIR, "freeze1.json"),
), (
    os.path.join(DATA_DIR, "freeze2.txt"),
    os.path.join(DATA_DIR, "freeze2.json"),
)]

HAS_PIP_PARAMS = [
    (os.path.join(DATA_DIR, "dev1.txt"), True),
    (os.path.join(DATA_DIR, "dev2.txt"), False),
    (os.path.join(DATA_DIR, "prod1.txt"), True),
    (os.path.join(DATA_DIR, "prod2.txt"), False),
]


# die, usage {{{1
def test_die():
    with pytest.raises(SystemExit):
        dephash.die("foo")


def test_usage():
    with pytest.raises(SystemExit):
        dephash.usage()


# run_cmd {{{1
def test_run_cmd_success():
    dephash.run_cmd("echo")


def test_run_cmd_failure():
    with pytest.raises(subprocess.CalledProcessError):
        dephash.run_cmd(['bash', '-c', 'exit 1'])


# rm {{{1
def test_nonexistent_rm():
    dephash.rm('this_file_does_not_exist_alksdjfalskjdfskfjdlk')


# to_str {{{1
@pytest.mark.parametrize("params", TO_STR_PARAMS, ids=TO_STR_IDS)
def test_to_str(params):
    val = dephash.to_str(params[0])
    assert val == params[1]


# get_output {{{1
@pytest.mark.parametrize("params", GET_OUTPUT_PARAMS, ids=GET_OUTPUT_IDS)
def test_get_output(params):
    output = dephash.get_output(params[0])
    assert output.rstrip() == params[1]


def test_get_output_error():
    with pytest.raises(subprocess.CalledProcessError):
        dephash.get_output(["bash", "-c", "echo foo && exit 1"])


# parse_pip_freeze {{{1
@pytest.mark.parametrize("params", PIP_FREEZE_PARAMS)
def test_parse_pip_freeze(params):
    output = read_file(params[0])
    module_dict = dephash.parse_pip_freeze(output)
    assert module_dict == load_json(params[1])


# has_pip {{{1
@pytest.mark.parametrize("params", HAS_PIP_PARAMS)
def test_has_pip(params):
    contents = read_file(params[0])
    assert dephash.has_pip(contents) is params[1]
