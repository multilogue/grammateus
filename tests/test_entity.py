# tests/test_entity.py

import unittest
import os
import tempfile
import shutil
import json
from ruamel.yaml import YAML
import jsonlines as jl # Import jsonlines for reading in tests

# Assuming your package structure allows this import
# If not, you might need to adjust sys.path or how you run tests
from src.grammateus.entity import Grammateus


# Helper function to read yaml safely
def read_yaml_records(file_path):
    yaml = YAML(typ='safe') # Use safe loader
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            if not content:
                return []
            f.seek(0)
            records = yaml.load(f)
            # Handle case where yaml.load returns None for empty/comment-only file
            return records if records is not None else []
    except FileNotFoundError:
        return []
    except Exception as e:
        print(f"Error reading YAML file {file_path}: {e}")
        return None # Indicate error

# Helper function to read jsonlines (handling potential errors)
def read_jsonlines_log(file_path):
    log = []
    try:
        with jl.open(file_path, 'r') as reader:
            for entry in reader:
                 log.append(entry) # jsonlines reader yields dicts
        return log
    except FileNotFoundError:
        return []
    except Exception as e: # Catch potential jl.JsonlinesError or others
        print(f"Error reading JSONLines file {file_path}: {e}")
        # Try reading raw lines if jsonlines fails, useful for debugging bad writes
        try:
            with open(file_path, 'r') as f:
                return [line.strip() for line in f.readlines()]
        except Exception:
            return None # Indicate error


class TestGrammateus(unittest.TestCase):

    def setUp(self):
        """Set up a temporary directory and file paths for each test."""
        self.test_dir = tempfile.mkdtemp()
        self.records_file_path = os.path.join(self.test_dir, 'test_records.yaml')
        self.log_file_path = os.path.join(self.test_dir, 'test_log.jsonl')
        # print(f"Setup: Created temp dir {self.test_dir}") # Optional: for debugging

    def tearDown(self):
        """Clean up the temporary directory after each test."""
        # print(f"Teardown: Removing temp dir {self.test_dir}") # Optional: for debugging
        shutil.rmtree(self.test_dir)

    def test_01_initialization_creates_files(self):
        """Test if files are created on initialization if they don't exist."""
        self.assertFalse(os.path.exists(self.records_file_path))
        self.assertFalse(os.path.exists(self.log_file_path))

        grammateus = Grammateus(
            records_path=self.records_file_path,
            log_path=self.log_file_path
        )

        self.assertTrue(os.path.exists(self.records_file_path))
        self.assertTrue(os.path.exists(self.log_file_path))
        # Check that files are empty initially
        self.assertEqual(os.path.getsize(self.records_file_path), 0)
        self.assertEqual(os.path.getsize(self.log_file_path), 0)
        # Check in-memory lists are empty
        self.assertEqual(grammateus.records, [])
        self.assertEqual(grammateus.log, [])

    def test_02_initialization_reads_existing_files(self):
        """Test if existing files are read correctly on initialization."""
        # Pre-populate records file
        initial_records = [{'record1': 'value1'}, {'record2': 'value2'}]
        yaml = YAML()
        yaml.indent(mapping=2, sequence=4, offset=2)
        with open(self.records_file_path, 'w') as f:
            yaml.dump(initial_records, f)

        # Pre-populate log file
        initial_log = [{'event': 'start'}, {'event': 'process', 'id': 1}]
        with jl.open(self.log_file_path, 'w') as writer:
            writer.write_all(initial_log)

        grammateus = Grammateus(
            records_path=self.records_file_path,
            log_path=self.log_file_path
        )

        # Check if the in-memory lists match the pre-populated data
        self.assertEqual(grammateus.records, initial_records)
        self.assertEqual(grammateus.log, initial_log)

    def test_03_record_it_dict(self):
        """Test recording a dictionary."""
        grammateus = Grammateus(records_path=self.records_file_path)
        record_data = {'key': 'value', 'number': 123}
        grammateus.record_it(record_data)

        # Verify in-memory list
        self.assertEqual(len(grammateus.records), 1)
        self.assertEqual(grammateus.records[0], record_data)

        # Verify file content (uses self.records_path now)
        file_records = read_yaml_records(self.records_file_path)
        self.assertEqual(len(file_records), 1)
        self.assertEqual(file_records[0], record_data)

    def test_04_record_it_string(self):
        """Test recording a JSON string."""
        grammateus = Grammateus(records_path=self.records_file_path)
        record_dict = {'message': 'hello from string', 'valid': True}
        record_string = json.dumps(record_dict)
        grammateus.record_it(record_string)

        # Verify in-memory list
        self.assertEqual(len(grammateus.records), 1)
        self.assertEqual(grammateus.records[0], record_dict)

        # Verify file content (uses self.records_path now)
        file_records = read_yaml_records(self.records_file_path)
        self.assertEqual(len(file_records), 1)
        self.assertEqual(file_records[0], record_dict)

    def test_05_record_it_append(self):
        """Test appending multiple records."""
        grammateus = Grammateus(records_path=self.records_file_path)
        record1 = {'id': 1, 'data': 'first'}
        record2_dict = {'id': 2, 'data': 'second'}
        record2_str = json.dumps(record2_dict)
        record3 = {'id': 3, 'data': 'third'}

        grammateus.record_it(record1)
        grammateus.record_it(record2_str)
        grammateus.record_it(record3)

        expected_records = [record1, record2_dict, record3]

        # Verify in-memory list
        self.assertEqual(len(grammateus.records), 3)
        self.assertEqual(grammateus.records, expected_records)

        # Verify file content
        file_records = read_yaml_records(self.records_file_path)
        self.assertEqual(len(file_records), 3)
        self.assertEqual(file_records, expected_records)

    def test_06_log_event_dict(self):
        """Test logging a dictionary event (checks for duplicate file write)."""
        grammateus = Grammateus(log_path=self.log_file_path)
        event_data = {'type': 'info', 'message': 'Process started'}
        grammateus.log_event(event_data)

        # Verify in-memory list (should have one entry)
        self.assertEqual(len(grammateus.log), 1)
        self.assertEqual(grammateus.log[0], event_data)

        # Verify file content (should have TWO entries due to bug in log_event)
        file_log = read_jsonlines_log(self.log_file_path)
        self.assertEqual(len(file_log), 2, "Expected duplicate entry in log file")
        self.assertEqual(file_log[0], event_data)
        self.assertEqual(file_log[1], event_data)

    def test_07_log_event_string(self):
        """Test logging a JSON string event (checks buggy behavior)."""
        grammateus = Grammateus(log_path=self.log_file_path, records_path=self.records_file_path) # Need both paths for this test
        event_dict = {'type': 'debug', 'details': 'Value calculated'}
        event_string = json.dumps(event_dict)
        grammateus.log_event(event_string)

        # Verify in-memory list (should have the dictionary)
        self.assertEqual(len(grammateus.log), 1)
        self.assertEqual(grammateus.log[0], event_dict)

        # Verify log file content (should contain the original STRING due to log_event's second write)
        # Note: jsonlines reader might fail here as it expects dicts per line. Read raw.
        with open(self.log_file_path, 'r') as f:
            log_lines = f.readlines()
        self.assertEqual(len(log_lines), 1, "Expected one line in log file")
        # The line written might be the raw string, potentially not valid JSON Lines format
        self.assertEqual(log_lines[0].strip(), event_string, "Log file should contain the original string")


        # Verify records file content (should contain the DICT due to bug in _log_one_json_string)
        record_file_content = read_yaml_records(self.records_file_path)
        self.assertEqual(len(record_file_content), 1, "Expected entry in records file due to bug")
        self.assertEqual(record_file_content[0], event_dict)


    def test_08_log_event_append(self):
        """Test appending multiple log events (checks combined buggy behavior)."""
        grammateus = Grammateus(log_path=self.log_file_path, records_path=self.records_file_path) # Need both paths
        event1 = {'timestamp': 't1', 'event': 'e1'}
        event2_dict = {'timestamp': 't2', 'event': 'e2'}
        event2_str = json.dumps(event2_dict)
        event3 = {'timestamp': 't3', 'event': 'e3'}

        grammateus.log_event(event1)     # Writes event1 twice to log file
        grammateus.log_event(event2_str) # Writes event2_dict to records, event2_str to log file
        grammateus.log_event(event3)     # Writes event3 twice to log file

        # Verify in-memory list (should be correct)
        expected_log_memory = [event1, event2_dict, event3]
        self.assertEqual(len(grammateus.log), 3)
        self.assertEqual(grammateus.log, expected_log_memory)

        # Verify log file content (complex due to bugs)
        # Expected: event1, event1, event2_str, event3, event3
        with open(self.log_file_path, 'r') as f:
            log_lines = [line.strip() for line in f.readlines()]

        self.assertEqual(len(log_lines), 5, "Expected 5 lines in log file due to bugs")
        self.assertEqual(json.loads(log_lines[0]), event1) # First write of event1 (as dict)
        self.assertEqual(json.loads(log_lines[1]), event1) # Second write of event1 (as dict)
        self.assertEqual(log_lines[2], event2_str)         # Second write of event2 (as string)
        self.assertEqual(json.loads(log_lines[3]), event3) # First write of event3 (as dict)
        self.assertEqual(json.loads(log_lines[4]), event3) # Second write of event3 (as dict)


        # Verify records file content (should contain event2_dict)
        record_file_content = read_yaml_records(self.records_file_path)
        self.assertEqual(len(record_file_content), 1, "Expected 1 entry in records file")
        self.assertEqual(record_file_content[0], event2_dict)


    def test_09_get_records(self):
        """Test retrieving records using get_records."""
        grammateus = Grammateus(records_path=self.records_file_path)
        record1 = {'id': 10}
        record2 = {'id': 20}
        grammateus.record_it(record1)
        grammateus.record_it(record2)

        # Add a record directly to the file using ruamel.yaml
        record3 = {'id': 30}
        current_records = read_yaml_records(self.records_file_path)
        current_records.append(record3)
        yaml = YAML()
        yaml.indent(mapping=2, sequence=4, offset=2)
        with open(self.records_file_path, 'w') as fw:
             yaml.dump(current_records, fw)

        # get_records should re-read the file
        retrieved_records = grammateus.get_records()
        expected_records = [record1, record2, record3]

        self.assertEqual(len(retrieved_records), 3)
        self.assertEqual(retrieved_records, expected_records)
        # Also check the internal state was updated
        self.assertEqual(grammateus.records, expected_records)

    def test_10_get_log(self):
        """Test retrieving the log using get_log."""
        grammateus = Grammateus(log_path=self.log_file_path)
        event1 = {'ev': 'a'}
        event2 = {'ev': 'b'}
        # Use _log_one directly to avoid log_event's duplicate write for this test
        grammateus._log_one(event1)
        grammateus._log_one(event2)

        # Add an event directly to the file
        event3 = {'ev': 'c'}
        with jl.open(self.log_file_path, 'a') as writer:
            writer.write(event3)

        # get_log should re-read the file
        retrieved_log = grammateus.get_log()
        expected_log = [event1, event2, event3]

        self.assertEqual(len(retrieved_log), 3)
        self.assertEqual(retrieved_log, expected_log)
        # Also check the internal state was updated
        self.assertEqual(grammateus.log, expected_log)

    def test_11_record_it_invalid_type(self):
        """Test recording an invalid type (just runs the code path)."""
        grammateus = Grammateus(records_path=self.records_file_path)
        # Currently prints "Wrong record type", doesn't raise error
        grammateus.record_it(12345)
        # No assertion possible without changing code or capturing stdout

    def test_12_log_event_invalid_type(self):
        """Test logging an invalid type (just runs the code path)."""
        grammateus = Grammateus(log_path=self.log_file_path)
         # Currently prints "Wrong record type", doesn't raise error
        grammateus.log_event(None)
        # No assertion possible without changing code or capturing stdout

    def test_13_record_one_json_string_invalid_json(self):
        """Test recording an invalid JSON string via _record_one_json_string."""
        grammateus = Grammateus(records_path=self.records_file_path)
        with self.assertRaisesRegex(Exception, 'can not convert record string to json'):
             # Accessing protected method for testing specific error case
            grammateus._record_one_json_string("this is not json")

    def test_14_log_one_json_string_invalid_json(self):
        """Test logging an invalid JSON string via _log_one_json_string."""
        # This test implicitly checks the bug where it tries to write to records_path
        grammateus = Grammateus(log_path=self.log_file_path, records_path=self.records_file_path)
        with self.assertRaisesRegex(Exception, 'can not convert record string to json'):
            # Accessing protected method for testing specific error case
            grammateus._log_one_json_string("{invalid json")

    def test_15_log_many_writes_to_records_path(self):
        """Test _log_many incorrectly writes to records_path and doesn't update self.log."""
        grammateus = Grammateus(log_path=self.log_file_path, records_path=self.records_file_path)
        events = [{'id': 1}, {'id': 2}, {'id': 3}]
        initial_log_state = list(grammateus.log) # Capture initial state

        # Accessing protected method
        grammateus._log_many(events)

        # Verify records file content (incorrect target)
        # Note: _log_many uses jsonlines writer on the YAML file path!
        # This will write jsonlines format into the records file.
        records_file_log = read_jsonlines_log(self.records_file_path)
        self.assertEqual(len(records_file_log), 3)
        self.assertEqual(records_file_log, events)

        # Verify log file content (should be empty)
        log_file_log = read_jsonlines_log(self.log_file_path)
        self.assertEqual(len(log_file_log), 0)

        # Verify in-memory list (should NOT be updated by _log_many)
        self.assertEqual(grammateus.log, initial_log_state)


if __name__ == '__main__':
    unittest.main()
