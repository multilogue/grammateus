# -*- coding: utf-8 -*-
# Python

"""Copyright (c) Alexander Fedotov.
This source code is licensed under the license found in the
LICENSE file in the root directory of this source tree.
"""
import pytest
from src.grammateus.entities import Grammateus


@pytest.fixture
def grammateus():
    return Grammateus()


class TestGrammateus:
    def test__init_records(self):
        assert False

    def test__read_records(self):
        assert False

    def test__init_log(self):
        assert False

    def test__read_log(self):
        assert False

    def test__log_one(self):
        assert False

    def test__log_one_json_string(self):
        assert False

    def test__log_many(self):
        assert False

    def test__record(self):
        assert False

    def test_log_it(self):
        assert False

    def test_get_log(self):
        assert False

    def test_record_it(self):
        assert False

    def test_get_records(self):
        assert False
