#!/usr/bin/env python
"""Test helper constants + functions
"""
import json
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def load_json(path):
    with open(path, "r") as fh:
        return json.load(fh)


def read_file(path):
    with open(path, "r") as fh:
        return fh.read()
