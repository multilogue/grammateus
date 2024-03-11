# -*- coding: utf-8 -*-
# Python

"""Copyright (c) Alexander Fedotov.
This source code is licensed under the license found in the
LICENSE file in the root directory of this source tree.
"""
import dotenv
dotenv.load_dotenv()
import pytest
from ..grammateus.entities import Grammateus


@pytest.fixture
def grammateus():
    return Grammateus(location='test_records.jsonl')


class TestGrammateus(grammateus):

    def test__record_one(self, grammateus):
        try:
            grammateus._record_one(record={"test": "test"})
        except Exception:
            assert False
        assert True

    def test__record_many(self):
        assert False
