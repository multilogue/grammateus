# tests/test_entity.py

import unittest
import os
import tempfile
import shutil
import json
from ruamel.yaml import YAML

# Assuming your package structure allows this import
# If not, you might need to adjust sys.path or how you run tests
from src.grammateus.entity import Grammateus

# Helper function to read yaml safely (similar to your original records_file.py)
def read_yaml_records(file_path):
    yaml = YAML(typ='safe') # Use safe loader
    try:
        with open(file_path, 'r') as f:
            # Handle empty file case
            content = f.read()
            if not content:
                return []
            # Reset pointer after read
            f.seek(0)
            records = yaml.load(f)
            return records if records else [] # Return empty list if file is empty/null
    except FileNotFoundError:
        return []
    except Exception as e:
        print(f"Error reading YAML file {file_path}: {e}")
        return None # Indicate error

# Helper function to read jsonlines
def read_jsonlines_log(file_path):
    log = []
    try:
        with open(file_path, 'r') as f:
            for line in f:
                try:
                    log.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    # Handle potential empty lines or malformed json if necessary
                    pass
        return log
    except FileNotFoundError:
        return []


class TestGrammateus(unittest.TestCase):

    def setUp(self):
        """Set up a temporary directory and file paths for each test."""
        # Create a temporary directory
        self.test_dir = tempfile.mkdtemp()
        # Define paths for test files within the temporary directory
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
        self.assertEqual(grammateus.records, []) # Should be empty list initially
        self.assertEqual(grammateus.log, [])     # Should be empty list initially

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
        with open(self.log_file_path, 'w') as f:
            for entry in initial_log:
                f.write(json.dumps(entry) + '\n')

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

        # Verify file content
        # NOTE: Assumes the bug fixing _record_one to write to self.records_path is done.
        # If not fixed, this check might need to look for 'data.yaml' instead.
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

        # Verify file content
        # NOTE: Assumes the bug fixing _record_one_json_string to write to self.records_path is done.
        file_records = read_yaml_records(self.records_file_path)
        self.assertEqual(len(file_records), 1)
        self.assertEqual(file_records[0], record_dict)

    def test_05_record_it_append(self):
        """Test appending multiple records."""
        grammateus = Grammateus(records_path=self.records_file_path)
        record1 = {'id': 1, 'data': 'first'}
        record2_str = json.dumps({'id': 2, 'data': 'second'})
        record3 = {'id': 3, 'data': 'third'}

        grammateus.record_it(record1)
        grammateus.record_it(record2_str)
        grammateus.record_it(record3)

        # Verify in-memory list
        self.assertEqual(len(grammateus.records), 3)
        self.assertEqual(grammateus.records[0], record1)
        self.assertEqual(grammateus.records[1], json.loads(record2_str))
        self.assertEqual(grammateus.records[2], record3)

        # Verify file content
        file_records = read_yaml_records(self.records_file_path)
        self.assertEqual(len(file_records), 3)
        self.assertEqual(file_records[0], record1)
        self.assertEqual(file_records[1], json.loads(record2_str))
        self.assertEqual(file_records[2], record3)

    def test_06_log_event_dict(self):
        """Test logging a dictionary event."""
        grammateus = Grammateus(log_path=self.log_file_path)
        event_data = {'type': 'info', 'message': 'Process started'}
        grammateus.log_event(event_data)

        # Verify in-memory list
        self.assertEqual(len(grammateus.log), 1)
        self.assertEqual(grammateus.log[0], event_data)

        # Verify file content
        # NOTE: Assumes the redundancy in log_event (writing twice) is fixed.
        # If not fixed, the file might contain the event twice.
        file_log = read_jsonlines_log(self.log_file_path)
        self.assertEqual(len(file_log), 1)
        self.assertEqual(file_log[0], event_data)

    def test_07_log_event_string(self):
        """Test logging a JSON string event."""
        grammateus = Grammateus(log_path=self.log_file_path)
        event_dict = {'type': 'debug', 'details': 'Value calculated'}
        event_string = json.dumps(event_dict)
        grammateus.log_event(event_string)

        # Verify in-memory list
        self.assertEqual(len(grammateus.log), 1)
        self.assertEqual(grammateus.log[0], event_dict)

        # Verify file content
        # NOTE: Assumes the redundancy in log_event (writing twice) is fixed.
        file_log = read_jsonlines_log(self.log_file_path)
        self.assertEqual(len(file_log), 1)
        self.assertEqual(file_log[0], event_dict)

    def test_08_log_event_append(self):
        """Test appending multiple log events."""
        grammateus = Grammateus(log_path=self.log_file_path)
        event1 = {'timestamp': 't1', 'event': 'e1'}
        event2_str = json.dumps({'timestamp': 't2', 'event': 'e2'})
        event3 = {'timestamp': 't3', 'event': 'e3'}

        grammateus.log_event(event1)
        grammateus.log_event(event2_str)
        grammateus.log_event(event3)

        # Verify in-memory list
        self.assertEqual(len(grammateus.log), 3)
        self.assertEqual(grammateus.log[0], event1)
        self.assertEqual(grammateus.log[1], json.loads(event2_str))
        self.assertEqual(grammateus.log[2], event3)

        # Verify file content
        file_log = read_jsonlines_log(self.log_file_path)
        self.assertEqual(len(file_log), 3)
        self.assertEqual(file_log[0], event1)
        self.assertEqual(file_log[1], json.loads(event2_str))
        self.assertEqual(file_log[2], event3)

    def test_09_get_records(self):
        """Test retrieving records using get_records."""
        grammateus = Grammateus(records_path=self.records_file_path)
        record1 = {'id': 10}
        record2 = {'id': 20}
        grammateus.record_it(record1)
        grammateus.record_it(record2)

        # Add a record directly to the file to simulate external modification
        # before calling get_records
        record3 = {'id': 30}
        with open(self.records_file_path, 'a') as f: # Need to append correctly
            # This manual append might not be perfect YAML, but tests reading
            # A better way would be to read, append, write using ruamel
            yaml = YAML()
            yaml.indent(mapping=2, sequence=4, offset=2)
            current_records = read_yaml_records(self.records_file_path)
            current_records.append(record3)
            with open(self.records_file_path, 'w') as fw:
                 yaml.dump(current_records, fw)


        # get_records should re-read the file
        retrieved_records = grammateus.get_records()

        self.assertEqual(len(retrieved_records), 3)
        self.assertEqual(retrieved_records[0], record1)
        self.assertEqual(retrieved_records[1], record2)
        self.assertEqual(retrieved_records[2], record3)
        # Also check the internal state was updated
        self.assertEqual(grammateus.records, retrieved_records)

    def test_10_get_log(self):
        """Test retrieving the log using get_log."""
        grammateus = Grammateus(log_path=self.log_file_path)
        event1 = {'ev': 'a'}
        event2 = {'ev': 'b'}
        grammateus.log_event(event1)
        grammateus.log_event(event2)

        # Add an event directly to the file
        event3 = {'ev': 'c'}
        with open(self.log_file_path, 'a') as f:
            f.write(json.dumps(event3) + '\n')

        # get_log should re-read the file
        retrieved_log = grammateus.get_log()

        self.assertEqual(len(retrieved_log), 3)
        self.assertEqual(retrieved_log[0], event1)
        self.assertEqual(retrieved_log[1], event2)
        self.assertEqual(retrieved_log[2], event3)
        # Also check the internal state was updated
        self.assertEqual(grammateus.log, retrieved_log)

    def test_11_record_it_invalid_type(self):
        """Test recording an invalid type (should ideally raise error or log warning)."""
        # Current implementation prints "Wrong record type"
        # A better implementation might raise a TypeError or log a warning.
        # This test currently doesn't assert anything but executes the path.
        grammateus = Grammateus(records_path=self.records_file_path)
        # Redirect stdout to check print? Or modify class to raise error?
        # For now, just call it.
        grammateus.record_it(12345)
        # Add assertion here if you modify the class behavior (e.g., assertRaises)

    def test_12_log_event_invalid_type(self):
        """Test logging an invalid type."""
        # Similar to record_it, currently prints "Wrong record type"
        grammateus = Grammateus(log_path=self.log_file_path)
        grammateus.log_event(None)
        # Add assertion here if you modify the class behavior

    def test_13_record_one_json_string_invalid_json(self):
        """Test recording an invalid JSON string."""
        grammateus = Grammateus(records_path=self.records_file_path)
        with self.assertRaisesRegex(Exception, 'can not sonvert record string to json'):
             # Note: Accessing protected method for testing specific error case
            grammateus._record_one_json_string("this is not json")

    def test_14_log_one_json_string_invalid_json(self):
        """Test logging an invalid JSON string."""
        grammateus = Grammateus(log_path=self.log_file_path)
        with self.assertRaisesRegex(Exception, 'can not sonvert record string to json'):
            # Note: Accessing protected method for testing specific error case
            grammateus._log_one_json_string("{invalid json")

    # Add test for _log_many if you intend to use/fix it
    # def test_15_log_many(self):
    #     """Test logging multiple events with _log_many."""
    #     # NOTE: This test assumes the bug in _log_many writing to
    #     # self.records_path instead of self.log_path is FIXED.
    #     grammateus = Grammateus(log_path=self.log_file_path)
    #     events = [{'id': 1}, {'id': 2}, {'id': 3}]
    #     # Note: Accessing protected method for testing
    #     grammateus._log_many(events)
    #
    #     # Verify file content (assuming fix is applied)
    #     file_log = read_jsonlines_log(self.log_file_path)
    #     self.assertEqual(len(file_log), 3)
    #     self.assertEqual(file_log, events)
    #
    #     # Verify in-memory list (current _log_many doesn't update self.log)
    #     # self.assertEqual(grammateus.log, events) # This would fail currently


if __name__ == '__main__':
    unittest.main()
