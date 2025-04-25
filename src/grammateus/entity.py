# -*- coding: utf-8 -*-
# Python

"""Copyright (c) Alexander Fedotov.
This source code is licensed under the license found in the
LICENSE file in the root directory of this source tree.
"""
import os
import json


default_base = os.getenv('GRAMMATEUS_LOCATION', './')


class Grammateus():
    yaml = None
    records_path = str
    records: list
    log_path = str
    log : list

    def __init__(self,
                 records_path=None,
                 log_path=None,
                 **kwargs):

        if records_path:
            from ruamel.yaml import YAML
            # initialize and configure ruamel.YAML
            self.yaml = YAML()
            self.yaml.preserve_quotes = True
            self.yaml.indent(mapping=2, sequence=4, offset=2)
            # check if records file exists, create it if not
            self.records_path = records_path
            self.records = []
            if os.path.exists(self.records_path):
                self._read_records()
            else:
                os.makedirs(os.path.dirname(self.records_path), exist_ok=True)
                open(self.records_path, 'w').close()
        if log_path:
            import jsonlines as jl
            self.jl = jl
            self.log_path = log_path
            self.log = []
            if os.path.exists(self.log_path):
                self._read_log()
            else:
                os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
                open(self.log_path, 'w').close()
        super(Grammateus, self).__init__(**kwargs)

    def _read_log(self):
        with self.jl.open(file=self.log_path, mode='r') as reader:
            self.log = list(reader)

    def _log_one(self, event: dict):
        self.log.append(event)
        with self.jl.open(file=self.log_path, mode='a') as writer:
            writer.write(event)

    def _log_one_json_string(self, event: str):
        try:
            event_dict = json.loads(event)
        except json.JSONDecodeError:
            raise Exception('can not sonvert record string to json')
        self.log.append(event_dict)
        with self.jl.open(file=self.records_path, mode='a') as writer:
            writer.write(event_dict)

    def _read_records(self):
        with open(file=self.records_path, mode='r') as file:
            self.records = self.yaml.load(file)

    def _record_one(self, record: dict):
        self.records.append(record)
        with open(self.records_path, 'r') as file:
            data = self.yaml.load(file) or []
        data.append(record)
        with open(self.records_path, 'w') as file:
            self.yaml.dump(data, file)

    def _record_one_json_string(self, record: str):
        try:
            record_dict = json.loads(record)
        except json.JSONDecodeError:
            raise Exception('can not convert record string to json')
        self.records.append(record_dict)
        with open(self.records_path, 'r') as file:
            data = self.yaml.load(file) or []
        data.append(record_dict)
        with open(self.records_path, 'w') as file:
            self.yaml.dump(data, file)

    def _log_many(self, events_list):
        with self.jl.open(file=self.records_path, mode='a') as writer:
            writer.write_all(events_list)

    def log_event(self, event: dict):
        if isinstance(event, dict):
            self._log_one(event)
        elif isinstance(event, str):
            self._log_one_json_string(event)
        else:
            print("Wrong record type")
        with self.jl.open(file=self.log_path, mode='a') as writer:
            writer.write(event)

    def get_log(self):
        self._read_log()
        return self.log

    def record_it(self, record):
        if isinstance(record, dict):
            self._record_one(record)
        elif isinstance(record, str):
            self._record_one_json_string(record)
        else:
            print("Wrong record type")

    def get_records(self):
        self._read_records()
        return self.records


if __name__ == '__main__':
    print('ok')