# -*- coding: utf-8 -*-
# Python

"""Copyright (c) Alexander Fedotov.
This source code is licensed under the license found in the
LICENSE file in the root directory of this source tree.
"""
import dotenv
dotenv.load_dotenv()
from json import dumps
import jsonlines
import pytest
from ..grammateus.entities import Grammateus


@pytest.fixture
def grammateus():
    return Grammateus(origin='anthropic', location='test_records.jsonl')


def test_record(grammateus):
    assert False


def test_log_event(grammateus):
    assert False


def test_get_records(grammateus):
    assert False
