# -*- coding: utf-8 -*-
# Python

"""Copyright (c) Alexander Fedotov.
This source code is licensed under the license found in the
LICENSE file in the root directory of this source tree.
"""
from os import path, getenv
# from pydantic import BaseModel
from json import loads, dumps
import jsonlines


default_base = getenv('GRAMMATEUS_LOCATION', './')


class Grammateus():
    location = str
    records = []

    def __init__(self,
                 location: str = 'records.jsonl',
                 **kwargs):
        self.location = f'{default_base}{location}'
        if path.exists(self.location):
            self._read_records()
        super(Grammateus, self).__init__(**kwargs)

    def _read_records(self):
        with jsonlines.open(file=self.location, mode='r') as reader:
            self.records = [line for line in reader.iter()]

    def _record_one(self, record: dict):
        serialized_record = dumps(record)
        with jsonlines.open(file=self.location,
                            mode='a') as writer:
            writer.write(serialized_record)

    def _record_many(self, records_list):
        with jsonlines.open(file=self.location,
                            mode='a') as writer:
            for record in records_list:
                serialized_record = dumps(record)
                writer.write(serialized_record)


class Librarian():
    location = str


    def __init__(self, location: str, **kwargs):
        self.location = location
        super(Librarian, self).__init__(**kwargs)


if __name__ == '__main__':
    gram =Grammateus(location='test_records.jsonl')
    print('ok')