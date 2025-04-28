# -*- coding: utf-8 -*-
# Python

"""Copyright (c) Alexander Fedotov.
This source code is licensed under the license found in the
LICENSE file in the root directory of this source tree.
"""
import os
import json
from ruamel.yaml import YAML
import jsonlines as jl

base_path = os.getenv('GRAMMATEUS_LOCATION', './')


class Grammateus:
    yaml = None
    jl = None
    records_path = str
    records: list
    log_path = str
    log : list

    def __init__(self, location=base_path, **kwargs):
        """ Initialize a new Grammateus instance for a new or existing records and log files.
        The records and log files will be created if they don't exist. If they do exist, they
        will be read and new records and log events will be appended to the files.

        You can configure Grammateus globally by setting the GRAMMATEUS_LOCATION env variable.

        :param location:  - a path to a directory where the records and log files are / will be;
        :param kwargs:    - you can pass the particular names of files in kwargs.
            'records_path' - a complete path of a records file f.i. '/home/user/gramms/records.yaml';
            'log_path' - a complete path of a log file f.i. '/home/user/gramms/log.jsonl';
        """
        # initialize and configure ruamel.YAML
        self.yaml = YAML()
        self.yaml.preserve_quotes = True
        self.yaml.indent(mapping=2, sequence=4, offset=2)

        # check if records file exists, create it if not
        if 'records_path' in kwargs:
            self.records_path = kwargs['records_path']
        else:
            self.records_path = location + 'records.yaml' if location else base_path + 'records.yaml'
        if os.path.exists(self.records_path):
            self._read_records()
        else:
            self._init_records()
        # logging
        self.jl = jl
        if 'log_path' in kwargs:
            self.log_path = kwargs['log_path']
        else:
            self.log_path = location + 'log.jsonl' if location else base_path + 'log.jsonl'
        if os.path.exists(self.log_path):
            self._read_log()
        else:
            self._init_log()
        super(Grammateus, self).__init__(**kwargs)

    def _init_records(self):
        os.makedirs(os.path.dirname(self.records_path), exist_ok=True)
        open(self.records_path, 'w').close()
        self.records = []

    def _init_log(self):
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
        open(self.log_path, 'w').close()
        self.log = []

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
            raise Exception('can not convert record string to json')
        self.log.append(event_dict)
        with self.jl.open(file=self.log_path, mode='a') as writer:
            writer.write(event_dict)

    def _log_many(self, events_list):
        self.log.extend(events_list)
        with self.jl.open(file=self.log_path, mode='a') as writer:
            writer.write_all(events_list)

    def _read_records(self):
        with open(file=self.records_path, mode='r') as file:
            self.records = self.yaml.load(file) or []

    def _record_one(self, record: dict):
        self.records.append(record)
        with open(self.records_path, 'r') as file:
            data = self.yaml.load(file) or []
        data.append(record)
        with open(self.records_path, 'w') as file:
            self.yaml.dump(data, file)

    def _record_many(self, records_list):
        self.records.extend(records_list)
        with open(self.records_path, 'r') as file:
            data = self.yaml.load(file) or []
        data.extend(records_list)
        with open(self.records_path, 'w') as file:
            self.yaml.dump(data, file)

    def _record_one_json_string(self, record: str):
        try:
            record_dict = json.loads(record)
        except json.JSONDecodeError:
            raise Exception('can not convert record string to json')
        self._record_one(record_dict)

    def log_it(self, what_to_log):
        if isinstance(what_to_log, dict):
            self._log_one(what_to_log)
        elif isinstance(what_to_log, str):
            self._log_one_json_string(what_to_log)
        elif isinstance(what_to_log, list):
            self._log_many(what_to_log)
        else:
            print("Wrong record type")

    def get_log(self):
        self._read_log()
        return self.log

    def record_it(self, record):
        if isinstance(record, dict):
            self._record_one(record)
        elif isinstance(record, str):
            self._record_one_json_string(record)
        elif isinstance(record, list):
            self._record_many(record)
        else:
            print("Wrong record type")

    def get_records(self):
        self._read_records()
        return self.records


class Scribe(Grammateus):
    """ Extended class that adds file and record maintenance operations to
        Grammateus functionality. Can work with its own files or with an
        existing Grammateus instance.
    """
    def __init__(self, source):
        """ Initialize with either a base_path to files (string)
        or an existing Grammateus instance.

        Args:
            source: Either a path string or a Grammateus instance
        """
        if isinstance(source, Grammateus):
            # Use existing Grammateus instance
            self.grammateus = source
        elif isinstance(source, str):
            # Create a new Grammateus instance internally
            super().__init__(source)
            self.grammateus = self
        else:
            raise TypeError("Source must be either a string path or a Grammateus instance")

    def records_to_log(self):
        records = self.grammateus.get_records()
        log = []
        for record in records:
            keys = record.keys()
            key = next(iter(record.keys()))
            if key == 'Human':
                user_said = dict(role='user', parts=[dict(text=record['Human'])])
                log.append(user_said)
            elif key == 'machine':
                text = record['machine']
                if isinstance(text, str):
                    utterance = text
                elif isinstance(text, list):
                    utterance = text[0]
                else:
                    utterance = ''
                    print('unknown record type')
                machine_said = dict(role='model', parts=[dict(text=utterance)])
                log.append(machine_said)
            else:
                print('unknown record type')
        # reset log
        self.grammateus._init_log()
        # add the recreated log
        self.grammateus.log_it(log)
        return self.grammateus.log


if __name__ == '__main__':
    # Test
    ...