# -*- coding: utf-8 -*-
# Python

"""Copyright (c) Alexander Fedotov.
This source code is licensed under the license found in the
LICENSE file in the root directory of this source tree.
"""
import yaml


def read_records(file_path):
    with open(file_path, 'r') as f:
        records = yaml.load(f, Loader=yaml.SafeLoader)

    for record in records:
        k, v = next(iter(record))


def write_records(file_path, records):
    with open(file_path, 'w') as f:
        yaml.dump(records, f, Dumper=yaml.SafeDumper)