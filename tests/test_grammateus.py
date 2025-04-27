# tests/test_grammateus.py
import os
import json
import shutil
import unittest
from unittest.mock import patch, mock_open, MagicMock

from src.grammateus.entities import Grammateus


class TestGrammateus(unittest.TestCase):
    """Test cases for the Grammateus class."""

    def setUp(self):
        """Set up test environment before each test."""
        self.test_dir = os.path.join(os.path.dirname(__file__), 'test_data/')
        os.makedirs(self.test_dir, exist_ok=True)
        self.grammateus = Grammateus(self.test_dir)

    def tearDown(self):
        """Clean up test environment after each test."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_init(self):
        """Test initialization creates directory and empty files."""
        self.assertTrue(os.path.exists(self.test_dir))
        self.assertTrue(os.path.exists(self.grammateus.records_path))
        self.assertTrue(os.path.exists(self.grammateus.log_path))
        self.assertEqual(self.grammateus.records, [])
        self.assertEqual(self.grammateus.log, [])

    def test_init_with_existing_files(self):
        """Test initialization with existing files."""
        # Create records file with some data
        yaml_content = "- id: 1\n  type: test_record\n  data: test_data\n"
        with open(self.grammateus.records_path, 'w') as f:
            f.write(yaml_content)

        # Create log file with some data
        with open(self.grammateus.log_path, 'w') as f:
            f.write('{"id": 1, "event": "test_event"}\n')
            f.write('{"id": 2, "event": "another_event"}\n')

        # Create new instance to test loading of existing files
        g = Grammateus(self.test_dir)

        # Verify records loaded
        self.assertEqual(len(g.records), 1)
        self.assertEqual(g.records[0]['id'], 1)
        self.assertEqual(g.records[0]['type'], 'test_record')

        # Verify log loaded
        self.assertEqual(len(g.log), 2)
        self.assertEqual(g.log[0]['id'], 1)
        self.assertEqual(g.log[1]['id'], 2)

    @patch('src.grammateus.entities.YAML')
    def test_read_records(self, mock_yaml_class):
        """Test reading records from YAML file."""
        mock_yaml = mock_yaml_class.return_value
        mock_yaml.load.return_value = [{"id": 1, "type": "test"}]

        self.grammateus._read_records()

        mock_yaml.load.assert_called_once()
        self.assertEqual(self.grammateus.records, [{"id": 1, "type": "test"}])

    @patch('src.grammateus.entities.jl.open')
    def test_read_log(self, mock_jl_open):
        """Test reading log from JSONL file."""
        mock_reader = MagicMock()
        mock_reader.__iter__.return_value = [{"id": 1, "event": "test"}, {"id": 2, "event": "test2"}]
        mock_jl_open.return_value.__enter__.return_value = mock_reader

        self.grammateus._read_log()

        mock_jl_open.assert_called_once_with(file=self.grammateus.log_path, mode='r')
        self.assertEqual(len(self.grammateus.log), 2)
        self.assertEqual(self.grammateus.log[0]["id"], 1)
        self.assertEqual(self.grammateus.log[1]["id"], 2)

    @patch('src.grammateus.entities.YAML')
    def test_record_one(self, mock_yaml_class):
        """Test recording a single record."""
        mock_yaml = mock_yaml_class.return_value
        mock_yaml.load.return_value = []

        record = {"id": 1, "type": "test_record"}
        self.grammateus._record_one(record)

        self.assertEqual(len(self.grammateus.records), 1)
        self.assertEqual(self.grammateus.records[0], record)
        mock_yaml.dump.assert_called_once()

    @patch('src.grammateus.entities.jl.open')
    def test_log_one(self, mock_jl_open):
        """Test logging a single event."""
        mock_writer = MagicMock()
        mock_jl_open.return_value.__enter__.return_value = mock_writer

        event = {"id": 1, "event": "test_event"}
        self.grammateus._log_one(event)

        self.assertEqual(len(self.grammateus.log), 1)
        self.assertEqual(self.grammateus.log[0], event)
        mock_writer.write.assert_called_once_with(event)

    @patch('src.grammateus.entities.json.loads')
    def test_record_one_json_string(self, mock_loads):
        """Test recording a record from JSON string."""
        mock_loads.return_value = {"id": 1, "type": "test_record"}

        with patch.object(self.grammateus, '_record_one') as mock_record_one:
            self.grammateus._record_one_json_string('{"id": 1, "type": "test_record"}')

            mock_loads.assert_called_once_with('{"id": 1, "type": "test_record"}')
            mock_record_one.assert_called_once_with({"id": 1, "type": "test_record"})

    @patch('src.grammateus.entities.json.loads')
    def test_record_one_json_string_error(self, mock_loads):
        """Test error handling when recording invalid JSON string."""
        mock_loads.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)

        with self.assertRaises(Exception) as context:
            self.grammateus._record_one_json_string('invalid json')

        self.assertIn('can not convert record string to json', str(context.exception))

    @patch('builtins.print')
    def test_record_it_invalid_type(self, mock_print):
        """Test handling of invalid record type."""
        self.grammateus.record_it(123)  # Neither dict nor string
        mock_print.assert_called_once_with("Wrong record type")

    def test_record_it_dict(self):
        """Test recording a dict record."""
        with patch.object(self.grammateus, '_record_one') as mock_record_one:
            record = {"id": 1, "type": "test"}
            self.grammateus.record_it(record)
            mock_record_one.assert_called_once_with(record)

    def test_record_it_string(self):
        """Test recording a string record."""
        with patch.object(self.grammateus, '_record_one_json_string') as mock_record_string:
            record_str = '{"id": 1, "type": "test"}'
            self.grammateus.record_it(record_str)
            mock_record_string.assert_called_once_with(record_str)

    def test_get_records(self):
        """Test retrieving records."""
        test_records = [{"id": 1, "type": "test"}]
        with patch.object(self.grammateus, '_read_records') as mock_read:
            self.grammateus.records = test_records
            records = self.grammateus.get_records()
            mock_read.assert_called_once()
            self.assertEqual(records, test_records)

    def test_get_log(self):
        """Test retrieving log events."""
        test_log = [{"id": 1, "event": "test"}]
        with patch.object(self.grammateus, '_read_log') as mock_read:
            self.grammateus.log = test_log
            log = self.grammateus.get_log()
            mock_read.assert_called_once()
            self.assertEqual(log, test_log)
