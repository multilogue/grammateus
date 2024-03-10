# -*- coding: utf-8 -*-
# Python

"""Copyright (c) Alexander Fedotov.
This source code is licensed under the license found in the
LICENSE file in the root directory of this source tree.
"""
from json import dumps, loads
from openai.types.chat import ChatCompletion


class OpenAIRecord:
    _record = []
    last_message: ChatCompletion = None

    def __init__(self, message: ChatCompletion):
        self.last_message = message
        self._record.append(dumps(self.last_message))

    def add_message(self, message: ChatCompletion):
        self.last_message = message
        self._record.append(dumps(self.last_message))

    def record(self):
        return self._record


class OpenAILog:
    location = str  # '/home/alxfed/Downloands/anthropic.log'
    _record = []

    def __init__(self, location: str):
        self.location = location
        self._read(location)

    def _read(self, location: str):
        with open(location, 'r') as f:
            self._record = loads(f.read())

    def record(self):
        return self._record
