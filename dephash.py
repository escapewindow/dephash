#!/usr/bin/env python
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from __future__ import absolute_import, division, print_function
import click
import logging
import os
import pprint
import re
import shutil
import six
import subprocess
import sys
import tempfile

log = logging.getLogger(__name__)

PACKAGE_REGEX = r"""^{module}-{version}(\.tar\.gz|-py[23]\..*\.whl)$"""
PIP_REGEX = r"""^pip[ >=<\d.]*(\\?$| *--hash)"""


# helper functions {{{1
def die(message, exit_code=1):
    """Print ``message`` on stderr, then exit ``exit_code``
    """
    log.error(message)
    sys.exit(exit_code)


def log_output(fh, log_level=logging.DEBUG):
    """Bare bones subprocess.Popen logger, with no streaming
    """
    output = fh.read()
    if not output:
        return
    if six.PY3 and isinstance(output, six.binary_type):  # pragma: no branch
        output = output.decode('utf-8')
    log.log(log_level, output)


def run_cmd(cmd, log_level=logging.DEBUG, **kwargs):
    """Print the command to run, then run it through ``subprocess.check_call``
    """
    log.debug("Running {}".format(cmd))
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, **kwargs)
    log_output(proc.stdout)
    proc.stdout.close()
    if proc.wait() is not 0:
        error = subprocess.CalledProcessError(proc.returncode, cmd)
        raise(error)


def to_str(obj):
    """Deal with bytes to unicode conversion in py3.
    """
    if six.PY3 and isinstance(obj, six.binary_type):
        obj = obj.decode('utf-8')
    return obj


def rm(path):
    if path is not None and os.path.isdir(path):
        log.debug("rmtree %s", path)
        shutil.rmtree(path)
    else:
        try:
            log.debug("removing %s", path)
            os.remove(path)
        except (OSError, TypeError):
            pass


def get_output(cmd, **kwargs):
    """Run ``cmd``, then raise ``subprocess.CalledProcessError`` on non-zero
    exit code, or return stdout text on zero exit code.
    """
    log.debug("Getting output from {}".format(cmd))
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


def get_pip_command(path_to_pip):
    return [path_to_pip, "--isolated"]


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
            print("# Generated from dephash.py + hashin.py", file=fh)
        for key, version in sorted(module_dict.items()):
            cmd = ["hashin", "{}=={}".format(key, version), tmppath, "sha512"]
            run_cmd(cmd)
        if req_prod_path is not None:
            rm(req_prod_path)
            log.debug("Writing to {}".format(req_prod_path))
            shutil.copyfile(tmppath, req_prod_path)
        else:
            with open(tmppath, "r") as fh:
                print(fh.read().rstrip())
    finally:
        rm(tmppath)


def has_pip(contents):
    """Try to see if ``pip`` is in the contents of this requirements file,
    since pip doesn't show up in the output of ``pip freeze``.
    """
    regex = re.compile(PIP_REGEX)
    for line in contents.split('\n'):
        if regex.match(line):
            return True
    return False


def create_virtualenv(virtualenv_cmd, venv_path, req_path):
    venv_cmd = [virtualenv_cmd, venv_path]
    run_cmd(venv_cmd)
    pip = get_pip_command(os.path.join(venv_path, 'bin', 'pip'))
    run_cmd(pip + ['install', '-r', req_path])


# cli {{{1
@click.group()
@click.option("-v", "--verbose", is_flag=True, help="Enable debug logging")
@click.option("-l", "--log-file", metavar="<logfile>", type=str, help="Specify a file to log to")
def cli(verbose, log_file):
    """Quick'n'dirty script to help with pinned python dependencies.
    """
    if verbose:
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.INFO)
    if log_file:
        log.addHandler(logging.FileHandler(log_file))
    else:
        if len(log.handlers) == 0:
            log.addHandler(logging.StreamHandler())


# outdated {{{1
@cli.command()
@click.option("--virtualenv", default='virtualenv', help="Path to virtualenv command")
@click.argument("path", type=click.Path(exists=True))
def outdated(virtualenv, path):
    """Find outdated packages in PATH, which can either be a requirements
    file or a virtualenv.
    """
    venv_path = None
    if os.path.isdir(path):
        venv_path = path
        tmp_path = None
    try:
        # create the virtualenv
        if venv_path is None:
            venv_path = tmp_path = tempfile.mkdtemp()
            create_virtualenv(virtualenv, venv_path, path)
        pip = get_pip_command(os.path.join(venv_path, 'bin', 'pip'))
        pip_output = get_output(pip + ['list', '--outdated']).rstrip()
        if pip_output:
            log.error("Found outdated packages in %s:", path)
            log.error(pip_output)
            sys.exit(1)
    finally:
        rm(tmp_path)


# gen {{{1
@cli.command()
@click.option("--virtualenv", default='virtualenv', help="Path to virtualenv command")
@click.option("-o", "--output-file", metavar="<requirements_prod>", type=click.Path(),
              help="Specify a file to write to; otherwise output to STDOUT")
@click.argument("requirements_dev")
def gen(virtualenv, output_file, requirements_dev):
    """Generate expanded python requirements, pinned to version+hashes.
    """
    venv_path = None
    try:
        # create the virtualenv
        venv_path = tempfile.mkdtemp()
        create_virtualenv(virtualenv, venv_path, requirements_dev)
        pip = get_pip_command(os.path.join(venv_path, 'bin', 'pip'))
        # get installed packages+versions
        pip_output = get_output(pip + ['freeze'])
        log.debug(pip_output)
        module_dict = parse_pip_freeze(pip_output)
        # special case pip, which doesn't show up in 'pip freeze'
        with open(requirements_dev, "r") as fh:
            if has_pip(fh.read()):
                pip_output = get_output(pip + ['--version'])
                pip_version = pip_output.split(' ')[1]
                module_dict['pip'] = pip_version
        log.debug(pprint.pformat(module_dict))
        # build hashed requirements file
        build_req_prod(module_dict, output_file)
        log.debug("Done.")
    finally:
        rm(venv_path)


# main {{{1
def main(name=None):
    # like ``if __name__ == '__main__':``, but easier to test
    if name in (None, '__main__'):
        return cli()


main(name=__name__)
