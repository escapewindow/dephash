#!/usr/bin/env python
"""Unittests for reqhash
"""
import os
import pytest
import reqhash
import six
import subprocess
import tempfile

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

GET_HASHES_PARAMS = [(
    os.path.join(DATA_DIR, "freeze_withpip1.json"),
    os.path.join(DATA_DIR, "hash1.txt"),
    os.path.join(DATA_DIR, "prod1.json"),
), (
    os.path.join(DATA_DIR, "freeze2.json"),
    os.path.join(DATA_DIR, "hash2.txt"),
    os.path.join(DATA_DIR, "prod2.json"),
)]

PRINT_PROD_REQ_PARAMS = [(
    os.path.join(DATA_DIR, "prod1.json"),
    os.path.join(DATA_DIR, "prod1.txt"),
), (
    os.path.join(DATA_DIR, "prod2.json"),
    os.path.join(DATA_DIR, "prod2.txt"),
)]

GET_PROD_PATH_PARAMS = [(
    os.path.join(DATA_DIR, "foo-dev.txt"),
    os.path.join(DATA_DIR, "foo-prod.txt"),
), (
    os.path.join(DATA_DIR, "foo-dv.txt"),
    os.path.join(DATA_DIR, "reqhash.out"),
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
    output = read_file(params[0])
    module_dict = reqhash.parse_pip_freeze(output)
    assert module_dict == load_json(params[1])


# get_hashes {{{1
@pytest.mark.parametrize("params", GET_HASHES_PARAMS)
def test_get_hashes(params):
    module_dict = load_json(params[0])
    output = read_file(params[1])
    result = load_json(params[2])
    reqhash.get_hashes(module_dict, output)
    assert module_dict == result


@pytest.mark.parametrize("params", GET_HASHES_PARAMS)
def test_get_hashes_broken(params):
    module_dict = load_json(params[0])
    output = read_file(params[1])
    module_dict["unknown-module"] = {"version": "unknown-version"}
    with pytest.raises(SystemExit):
        reqhash.get_hashes(module_dict, output)


# print_prod_req {{{1
@pytest.mark.parametrize("params", PRINT_PROD_REQ_PARAMS)
def test_print_prod_req(params):
    module_dict = load_json(params[0])
    _, path = tempfile.mkstemp()
    try:
        with open(path, "w") as fh:
            reqhash.print_prod_req(module_dict, fh)
        with open(path, "r") as fh:
            contents = fh.read()
    finally:
        fh.close()
        os.remove(path)
    assert contents == read_file(params[1])


# get_prod_path {{{1
@pytest.mark.parametrize("params", GET_PROD_PATH_PARAMS)
def test_get_prod_path(params):
    assert reqhash.get_prod_path(params[0]) == params[1]


# has_pip {{{1
@pytest.mark.parametrize("params", HAS_PIP_PARAMS)
def test_has_pip(params):
    contents = read_file(params[0])
    assert reqhash.has_pip(contents) is params[1]
