#!/usr/bin/env python
from __future__ import absolute_import, division, print_function
import glob
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
PIP_REGEX = r"""^pip[ >=<\d.]*$"""


# helper functions {{{1
def die(message, exit_code=1):
    print(message, file=sys.stderr)
    sys.exit(exit_code)


def usage():
    die("Usage: {} REQUIREMENTS_PATH".format(sys.argv[0]))


def run_cmd(cmd, **kwargs):
    print("Running {}".format(cmd))
    return subprocess.check_call(cmd, **kwargs)


def to_str(obj):
    if six.PY3 and isinstance(obj, six.binary_type):
        obj = obj.decode('utf-8')
    return obj


def get_output(cmd, **kwargs):
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
    module_dict = {}
    for line in output.rstrip().split('\n'):
        module, version = line.split('==')
        module_dict[module] = {'version': version}
    return module_dict


def get_hashes(module_dict, output):
    # create a dict from the output
    messages = []
    lines = output.rstrip().split('\n')
    it = iter(lines)
    hashes = dict([(x.rstrip(':'), y.lstrip()) for x, y in zip(it, it)])
    pprint.pprint(hashes)
    for module, defn in module_dict.items():
        regex_module = module.replace('-', '[_-]')
        regex_string = PACKAGE_REGEX.format(module=regex_module,
                                            version=defn['version'])
        print(regex_string)
        regex = re.compile(regex_string)
        for filename, hashstring in hashes.items():
            if regex.match(filename) is not None:
                module_dict[module]['hash'] = hashstring
                break
        else:
            messages.append("Can't find hash for {}!".format(module))
    if messages:
        die('\n'.join(messages))


def print_prod_req(module_dict, fh):
    print("# Generated from reqhash.py", file=fh)
    for module, defn in sorted(module_dict.items()):
        print("{}=={} {}".format(module, defn['version'], defn['hash']),
              file=fh)


def get_prod_path(req_dev_path):
    parent_dir = os.path.dirname(req_dev_path)
    dev_name = os.path.basename(req_dev_path)
    if '-dev' in dev_name:
        prod_name = dev_name.replace('-dev', '-prod')
    else:
        prod_name = 'reqhash.out'
    return os.path.join(parent_dir, prod_name)


def has_pip(contents):
    regex = re.compile(PIP_REGEX)
    for line in contents.split('\n'):
        if regex.match(line):
            return True


# main {{{1
def main(name=None):
    if name not in (None, '__main__'):
        return
    if len(sys.argv) != 2:
        usage()
    tempdir = None
    venv_path = None
    try:
        # get the absolute path of the dev requirements file, since we'll
        # chdir later
        req_dev_path = os.path.abspath(sys.argv[1])
        # create tempdirs
        venv_path = tempfile.mkdtemp()
        tempdir = tempfile.mkdtemp()
        os.chdir(tempdir)
        # download all the dependencies
        sys.argv = ['pip', 'download', '-r', req_dev_path]
        pip_main()
        # create the virtualenv
        sys.argv = ['virtualenv', venv_path]
        virtualenv_main()
        pip = os.path.join(venv_path, 'bin', 'pip')
        file_list = glob.glob('*')
        # install deps and get their versions
        run_cmd([pip, 'install', '--no-deps'] + file_list)
        output = get_output([pip, 'freeze'])
        print(output)
        module_dict = parse_pip_freeze(output)
        # special case pip, which doesn't show up in 'pip freeze'
        with open(req_dev_path, "r") as fh:
            if has_pip(fh.read()):
                output = get_output([pip, '--version'])
                pip_version = output.split(' ')[1]
                module_dict['pip'] = {'version': pip_version}
        print(pprint.pformat(module_dict))
        # get hashes from the downloaded files
        output = get_output([pip, 'hash', '--algorithm', 'sha512'] + file_list)
        print(output)
        get_hashes(module_dict, output)
        pprint.pprint(module_dict)
        req_prod_path = get_prod_path(req_dev_path)
        print("Writing pinned+hashed requirements to {}".format(req_prod_path))
        print_prod_req(module_dict, sys.stdout)
        with open(req_prod_path, "w") as fh:
            print_prod_req(module_dict, fh)
        print("Done.")
    finally:
        for path in (tempdir, venv_path):
            if path is not None and os.path.exists(path):
                shutil.rmtree(path)


main(name=__name__)
