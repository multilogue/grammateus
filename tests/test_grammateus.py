# -*- coding: utf-8 -*-
# Python

"""Copyright (c) Alexander Fedotov.
This source code is licensed under the license found in the
LICENSE file in the root directory of this source tree.
"""
import os
import json
import pytest
import yaml
import jsonlines as jl
from unittest.mock import patch, mock_open, MagicMock, call
from src.grammateus.entities import Grammateus


@pytest.fixture
def temp_dir(tmpdir):
    """Fixture to provide a temporary directory for file operations."""
    return tmpdir.strpath + '/'


@pytest.fixture
def sample_records():
    """Fixture to provide sample records of utterances."""
    return [
        {"Human": "I would like you to say something"},
        {"machine": "It's a beautiful day today, isn't it?"}
    ]


@pytest.fixture
def sample_log():
    """Fixture to provide sample log events."""
    return [
        {"role": "user", "content": "I would like you to say something"},
        {"role": "model", "content": "It's a beautiful day today, isn't it?"}
    ]


class TestGrammateus:
    def test__init__(self, temp_dir):
        """Test Grammateus initialization with various parameters."""
        # Test with default parameters
        with patch('os.path.exists') as mock_exists, \
                patch.object(Grammateus, '_read_records') as mock_read_records, \
                patch.object(Grammateus, '_read_log') as mock_read_log, \
                patch.object(Grammateus, '_init_records') as mock_init_records, \
                patch.object(Grammateus, '_init_log') as mock_init_log:
            # Case 1: Both files exist
            mock_exists.return_value = True
            g = Grammateus()
            assert g.records_path.endswith('records.yaml')
            assert g.log_path.endswith('log.jsonl')
            mock_read_records.assert_called_once()
            mock_read_log.assert_called_once()
            mock_init_records.assert_not_called()
            mock_init_log.assert_not_called()

            # Reset mocks
            mock_exists.reset_mock()
            mock_read_records.reset_mock()
            mock_read_log.reset_mock()
            mock_init_records.reset_mock()
            mock_init_log.reset_mock()

            # Case 2: No files exist
            mock_exists.return_value = False
            g = Grammateus()
            mock_init_records.assert_called_once()
            mock_init_log.assert_called_once()
            mock_read_records.assert_not_called()
            mock_read_log.assert_not_called()

        # Test with custom location
        with patch('os.path.exists') as mock_exists, \
                patch.object(Grammateus, '_read_records') as mock_read_records, \
                patch.object(Grammateus, '_init_records') as mock_init_records, \
                patch.object(Grammateus, '_read_log') as mock_read_log, \
                patch.object(Grammateus, '_init_log') as mock_init_log:
            mock_exists.return_value = True
            g = Grammateus(location=temp_dir)
            assert g.records_path == temp_dir + 'records.yaml'
            assert g.log_path == temp_dir + 'log.jsonl'

        # Test with custom file paths
        with patch('os.path.exists') as mock_exists, \
                patch.object(Grammateus, '_read_records') as mock_read_records, \
                patch.object(Grammateus, '_init_records') as mock_init_records, \
                patch.object(Grammateus, '_read_log') as mock_read_log, \
                patch.object(Grammateus, '_init_log') as mock_init_log:
            mock_exists.return_value = True
            custom_records_path = temp_dir + 'custom_records.yaml'
            custom_log_path = temp_dir + 'custom_log.jsonl'

            g = Grammateus(records_path=custom_records_path, log_path=custom_log_path)
            assert g.records_path == custom_records_path
            assert g.log_path == custom_log_path

    def test__init_records(self, temp_dir):
        """Test records initialization."""
        with patch('os.makedirs') as mock_makedirs, \
                patch('builtins.open', mock_open()) as mock_file:
            g = Grammateus()
            # Reset to call _init_records explicitly
            g.records_path = temp_dir + 'records.yaml'
            g._init_records()

            # Verify that directories were created
            mock_makedirs.assert_called_once_with(os.path.dirname(g.records_path), exist_ok=True)
            # Verify file was created
            mock_file.assert_called_once_with(g.records_path, 'w')
            # Verify records list was initialized
            assert g.records == []

    def test__read_records(self, sample_records):
        """Test reading records from file."""
        with patch('builtins.open', mock_open(read_data="dummy yaml content")), \
                patch('yaml.load', return_value=sample_records) as mock_yaml_load:
            g = Grammateus()
            g._read_records()

            # Check yaml.load was called
            mock_yaml_load.assert_called_once()
            # Check that records were properly loaded
            assert g.records == sample_records

    def test__read_records_empty_file(self):
        """Test reading records from an empty file."""
        with patch('builtins.open', mock_open(read_data="")), \
                patch('yaml.load', return_value=None) as mock_yaml_load:
            g = Grammateus()
            g._read_records()

            # Check yaml.load was called
            mock_yaml_load.assert_called_once()
            # Check that records were initialized as empty list
            assert g.records == []

    def test__init_log(self, temp_dir):
        """Test log initialization."""
        with patch('os.makedirs') as mock_makedirs, \
                patch('builtins.open', mock_open()) as mock_file:
            g = Grammateus()
            # Reset to call _init_log explicitly
            g.log_path = temp_dir + 'log.jsonl'
            g._init_log()

            # Verify that directories were created
            mock_makedirs.assert_called_once_with(os.path.dirname(g.log_path), exist_ok=True)
            # Verify file was created
            mock_file.assert_called_once_with(g.log_path, 'w')
            # Verify log list was initialized
            assert g.log == []

    def test__read_log(self, sample_log):
        """Test reading log from file."""
        # Create mock for jsonlines.open
        mock_jl_reader = MagicMock()
        mock_jl_reader.__enter__.return_value = sample_log

        with patch('jsonlines.open', return_value=mock_jl_reader) as mock_jl_open:
            g = Grammateus()

            # Mock list() to return sample_log when called on the reader
            with patch('builtins.list', return_value=sample_log):
                g._read_log()

            # Check jsonlines.open was called
            mock_jl_open.assert_called_once_with(file=g.log_path, mode='r')
            # Check that log was properly loaded
            assert g.log == sample_log

    def test__log_one(self):
        """Test logging a single event."""
        event = {"event_type": "message", "content": "Test message"}
        mock_writer = MagicMock()

        with patch('jsonlines.open', return_value=mock_writer) as mock_jl_open:
            g = Grammateus()
            g.log = []
            g._log_one(event)

            # Check that event was added to log
            assert g.log == [event]
            # Check jsonlines.open was called
            mock_jl_open.assert_called_once_with(file=g.log_path, mode='a')
            # Check that write was called on the writer
            mock_writer.__enter__.return_value.write.assert_called_once_with(event)

    def test__log_one_json_string(self):
        """Test logging a single event from a JSON string."""
        event_str = '{"event_type": "message", "content": "Test message"}'
        event_dict = json.loads(event_str)
        mock_writer = MagicMock()

        with patch('jsonlines.open', return_value=mock_writer) as mock_jl_open:
            g = Grammateus()
            g.log = []
            g._log_one_json_string(event_str)

            # Check that event was added to log
            assert g.log == [event_dict]
            # Check jsonlines.open was called
            mock_jl_open.assert_called_once_with(file=g.log_path, mode='a')
            # Check that write was called on the writer
            mock_writer.__enter__.return_value.write.assert_called_once_with(event_dict)

    def test__log_one_json_string_invalid(self):
        """Test logging an invalid JSON string."""
        invalid_event_str = '{"event_type": "message", "content": "Test message'

        g = Grammateus()
        g.log = []

        # Should raise an exception
        with pytest.raises(Exception) as excinfo:
            g._log_one_json_string(invalid_event_str)

        assert "can not convert record string to json" in str(excinfo.value)
        # Check that log was not modified
        assert g.log == []

    def test__log_many(self):
        """Test logging multiple events."""
        events = [
            {"event_type": "message", "content": "First message"},
            {"event_type": "response", "content": "First response"}
        ]
        mock_writer = MagicMock()

        with patch('jsonlines.open', return_value=mock_writer) as mock_jl_open:
            g = Grammateus()
            g.log = []
            g._log_many(events)

            # Check that events were added to log
            assert g.log == events
            # Check jsonlines.open was called
            mock_jl_open.assert_called_once_with(file=g.log_path, mode='a')
            # Check that write_all was called on the writer
            mock_writer.__enter__.return_value.write_all.assert_called_once_with(events)

    def test__record(self, sample_records):
        """Test recording to file."""
        with patch('builtins.open', mock_open()) as mock_file, \
                patch('yaml.dump') as mock_yaml_dump:
            g = Grammateus()
            g.records = sample_records
            g._record()

            # Check open was called
            mock_file.assert_called_once_with(g.records_path, 'w')
            # Check yaml.dump was called with the records
            mock_yaml_dump.assert_called_once_with(sample_records, mock_file().__enter__(), Dumper=yaml.Dumper)

    def test_log_it_dict(self):
        """Test log_it with a dictionary."""
        event = {"event_type": "message", "content": "Test message"}

        with patch.object(Grammateus, '_log_one') as mock_log_one:
            g = Grammateus()
            g.log_it(event)

            # Check _log_one was called with the event
            mock_log_one.assert_called_once_with(event)

    def test_log_it_str(self):
        """Test log_it with a string."""
        event_str = '{"event_type": "message", "content": "Test message"}'

        with patch.object(Grammateus, '_log_one_json_string') as mock_log_one_json_string:
            g = Grammateus()
            g.log_it(event_str)

            # Check _log_one_json_string was called with the event string
            mock_log_one_json_string.assert_called_once_with(event_str)

    def test_log_it_list(self):
        """Test log_it with a list."""
        events = [
            {"event_type": "message", "content": "First message"},
            {"event_type": "response", "content": "First response"}
        ]

        with patch.object(Grammateus, '_log_many') as mock_log_many:
            g = Grammateus()
            g.log_it(events)

            # Check _log_many was called with the events list
            mock_log_many.assert_called_once_with(events)

    def test_log_it_invalid_type(self, capsys):
        """Test log_it with an invalid type."""
        invalid_event = 42  # Integer is not a valid type

        g = Grammateus()
        g.log_it(invalid_event)

        # Check the printed output
        captured = capsys.readouterr()
        assert "Wrong record type" in captured.out

    def test_get_log(self, sample_log):
        """Test get_log method."""
        with patch.object(Grammateus, '_read_log') as mock_read_log:
            g = Grammateus()
            g.log = sample_log
            result = g.get_log()

            # Check _read_log was called
            mock_read_log.assert_called_once()
            # Check the returned result
            assert result == sample_log

    def test_record_it_dict(self):
        """Test record_it with a dictionary."""
        record = {"id": 3, "text": "New record"}

        with patch.object(Grammateus, '_read_records') as mock_read_records, \
                patch.object(Grammateus, '_record') as mock_record:
            g = Grammateus()
            g.records = []
            g.record_it(record)

            # Check _read_records was called
            mock_read_records.assert_called_once()
            # Check record was added to records
            assert g.records == [record]
            # Check _record was called
            mock_record.assert_called_once()

    def test_record_it_str(self):
        """Test record_it with a string."""
        record_str = '{"id": 3, "text": "New record"}'
        record_dict = json.loads(record_str)

        with patch.object(Grammateus, '_read_records') as mock_read_records, \
                patch.object(Grammateus, '_record') as mock_record:
            g = Grammateus()
            g.records = []
            g.record_it(record_str)

            # Check _read_records was called
            mock_read_records.assert_called_once()
            # Check record was added to records
            assert g.records == [record_dict]
            # Check _record was called
            mock_record.assert_called_once()

    def test_record_it_str_invalid(self):
        """Test record_it with an invalid string."""
        invalid_record_str = '{"id": 3, "text": "New record'

        with patch.object(Grammateus, '_read_records') as mock_read_records:
            g = Grammateus()
            g.records = []

            # Should raise an exception
            with pytest.raises(Exception) as excinfo:
                g.record_it(invalid_record_str)

            assert "can not convert record string to json" in str(excinfo.value)
            # Check _read_records was called
            mock_read_records.assert_called_once()
            # Check records was not modified
            assert g.records == []

    def test_record_it_list(self):
        """Test record_it with a list."""
        records = [
            {"id": 3, "text": "Record 3"},
            {"id": 4, "text": "Record 4"}
        ]

        with patch.object(Grammateus, '_read_records') as mock_read_records, \
                patch.object(Grammateus, '_record') as mock_record:
            g = Grammateus()
            g.records = []
            g.record_it(records)

            # Check _read_records was called
            mock_read_records.assert_called_once()
            # Check records were added to records
            assert g.records == records
            # Check _record was called
            mock_record.assert_called_once()

    def test_record_it_invalid_type(self, capsys):
        """Test record_it with an invalid type."""
        invalid_record = 42  # Integer is not a valid type

        with patch.object(Grammateus, '_read_records') as mock_read_records:
            g = Grammateus()
            g.records = []
            g.record_it(invalid_record)

            # Check _read_records was called
            mock_read_records.assert_called_once()
            # Check the printed output
            captured = capsys.readouterr()
            assert "Wrong record type" in captured.out
            # Check records was not modified
            assert g.records == []

    def test_get_records(self, sample_records):
        """Test get_records method."""
        with patch.object(Grammateus, '_read_records') as mock_read_records:
            g = Grammateus()
            g.records = sample_records
            result = g.get_records()

            # Check _read_records was called
            mock_read_records.assert_called_once()
            # Check the returned result
            assert result == sample_records