#!/usr/bin/env python
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from __future__ import absolute_import, division, print_function
import os
from pip import main as pip_main
import pprint
import re
import shutil
import six
import subprocess
import sys
import tempfile
from virtualenv import main as virtualenv_main

PACKAGE_REGEX = r"""^{module}-{version}(\.tar\.gz|-py[23]\..*\.whl)$"""
PIP_REGEX = r"""^pip[ >=<\d.]*(\\?$| *--hash)"""


# helper functions {{{1
def die(message, exit_code=1):
    """Print ``message`` on stderr, then exit ``exit_code``
    """
    print(message, file=sys.stderr)
    sys.exit(exit_code)


def usage():
    """Shortcut function to print usage and die
    """
    die("Usage: {} REQUIREMENTS_PATH".format(sys.argv[0]))


def run_cmd(cmd, **kwargs):
    """Print the command to run, then run it through ``subprocess.check_call``
    """
    print("Running {}".format(cmd))
    return subprocess.check_call(cmd, **kwargs)


def to_str(obj):
    """Deal with bytes to unicode conversion in py3.
    """
    if six.PY3 and isinstance(obj, six.binary_type):
        obj = obj.decode('utf-8')
    return obj


def rm(path):
    if path is not None and os.path.isdir(path):
        shutil.rmtree(path)
    else:
        try:
            os.remove(path)
        except (OSError, TypeError):
            pass


def get_output(cmd, **kwargs):
    """Run ``cmd``, then raise ``subprocess.CalledProcessError`` on non-zero
    exit code, or return stdout text on zero exit code.
    """
    print("Getting output from {}".format(cmd))
    try:
        outfile = tempfile.TemporaryFile()
        proc = subprocess.Popen(cmd, stdout=outfile, **kwargs)
        rc = proc.wait()
        outfile.seek(0)
        output = to_str(outfile.read())
        if rc == 0:
            return output
        else:
            error = subprocess.CalledProcessError(proc.returncode, cmd)
            error.output = error
            raise error
    finally:
        outfile.close()


def parse_pip_freeze(output):
    """Take the output from ``pip freeze`` and return a dictionary in the form
    of

        {module_name: version, ...}
    """
    module_dict = {}
    for line in output.rstrip().split('\n'):
        module, version = line.split('==')
        module_dict[module] = version
    return module_dict


def build_req_prod(module_dict, req_prod_path):
    """Use ``hashin`` and the dictionary from ``pip freeze`` to build a new
    requirements file at req_prod_path
    """
    try:
        _, tmppath = tempfile.mkstemp(text=True)
        with open(tmppath, "w") as fh:
            print("# Generated from reqhash.py + hashin.py", file=fh)
        for key, version in sorted(module_dict.items()):
            cmd = ["hashin", "{}=={}".format(key, version), tmppath, "sha512"]
            run_cmd(cmd)
        rm(req_prod_path)
        print("Writing to {}".format(req_prod_path))
        shutil.copyfile(tmppath, req_prod_path)
        with open(req_prod_path, "r") as fh:
            print(fh.read())
    finally:
        rm(tmppath)


# TODO argparse this
def get_prod_path(req_dev_path):
    """Given a development requirements.txt path, build a production
    requirements.txt path.  This just replaces ``-dev`` with ``-prod``,
    defaulting to ``reqhash.out`` if ``-dev`` isn't in the ``req_dev_path``
    basename.
    """
    parent_dir = os.path.dirname(req_dev_path)
    dev_name = os.path.basename(req_dev_path)
    if '-dev' in dev_name:
        prod_name = dev_name.replace('-dev', '-prod')
    else:
        prod_name = 'reqhash.out'
    return os.path.join(parent_dir, prod_name)


def has_pip(contents):
    """Try to see if ``pip`` is in the contents of this requirements file,
    since pip doesn't show up in the output of ``pip freeze``.
    """
    regex = re.compile(PIP_REGEX)
    for line in contents.split('\n'):
        if regex.match(line):
            return True
    return False


# main {{{1
def main(name=None):
    """the main shebang
    """
    # like ``if __name__ == '__main__':``, but easier to test
    if name not in (None, '__main__'):
        return
    if len(sys.argv) != 2:
        usage()
    req_dev_path = sys.argv[1]
    venv_path = None
    try:
        # create the virtualenv
        venv_path = tempfile.mkdtemp()
        sys.argv = ['virtualenv', venv_path]
        virtualenv_main()
        pip = [os.path.join(venv_path, 'bin', 'pip'), '--isolated']
        # install deps and get their versions
        run_cmd(pip + ['install', '-r', req_dev_path])
        output = get_output(pip + ['freeze'])
        print(output)
        module_dict = parse_pip_freeze(output)
        # special case pip, which doesn't show up in 'pip freeze'
        with open(req_dev_path, "r") as fh:
            if has_pip(fh.read()):
                output = get_output(pip + ['--version'])
                pip_version = output.split(' ')[1]
                module_dict['pip'] = pip_version
        print(pprint.pformat(module_dict))
        # get hashes from the downloaded files
        req_prod_path = get_prod_path(req_dev_path)
        build_req_prod(module_dict, req_prod_path)
        print("Done.")
    finally:
        rm(venv_path)


main(name=__name__)
