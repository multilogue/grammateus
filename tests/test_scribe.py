# -*- coding: utf-8 -*-
# Python

"""Copyright (c) Alexander Fedotov.
This source code is licensed under the license found in the
LICENSE file in the root directory of this source tree.
"""
# tests/test_scribe.py
import os
import json
import shutil
import unittest
from unittest.mock import patch, MagicMock

from src.grammateus.entities import Grammateus, Scribe


class TestScribe(unittest.TestCase):
    """Test cases for the Scribe class."""

    def setUp(self):
        """Set up test environment before each test."""
        self.test_dir = os.path.join(os.path.dirname(__file__), 'test_data')
        os.makedirs(self.test_dir, exist_ok=True)
        self.grammateus = Grammateus(self.test_dir)

        # Add some test records
        self.grammateus._records = [
            {
                "id": 1,
                "timestamp": "2023-01-01T12:00:00",
                "type": "login",
                "data": {"user": "test_user"}
            },
            {
                "id": 2,
                "timestamp": "2023-01-01T12:30:00",
                "type": "action",
                "data": {"action": "test_action"}
            }
        ]
        self.grammateus.save_records()

    def tearDown(self):
        """Clean up test environment after each test."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_init_with_path(self):
        """Test initialization with path."""
        scribe = Scribe(self.test_dir)
        self.assertIsInstance(scribe.grammateus, Grammateus)
        self.assertEqual(scribe.grammateus, scribe)  # self-reference
        self.assertEqual(len(scribe.grammateus._records), 2)

    def test_init_with_grammateus(self):
        """Test initialization with Grammateus instance."""
        scribe = Scribe(self.grammateus)
        self.assertEqual(scribe.grammateus, self.grammateus)
        self.assertEqual(len(scribe.grammateus._records), 2)

    def test_init_invalid(self):
        """Test initialization with invalid input."""
        with self.assertRaises(TypeError):
            Scribe(123)  # Neither string nor Grammateus

    def test_delete_record(self):
        """Test deleting a record."""
        scribe = Scribe(self.grammateus)
        result = scribe.delete_record(1)

        self.assertTrue(result)
        self.assertEqual(len(self.grammateus._records), 1)
        self.assertEqual(self.grammateus._records[0]["id"], 2)

    def test_delete_record_nonexistent(self):
        """Test deleting a nonexistent record."""
        scribe = Scribe(self.grammateus)
        result = scribe.delete_record(999)

        self.assertFalse(result)
        self.assertEqual(len(self.grammateus._records), 2)

    def test_update_record(self):
        """Test updating a record."""
        scribe = Scribe(self.grammateus)

        with patch('src.grammateus.entities.datetime') as mock_datetime:
            mock_datetime.now.return_value.isoformat.return_value = "2023-01-01T13:00:00"
            result = scribe.update_record(2, {"new_field": "new_value"})

        self.assertTrue(result)
        updated_record = self.grammateus._records[1]
        self.assertEqual(updated_record["data"]["new_field"], "new_value")
        self.assertEqual(updated_record["data"]["action"], "test_action")  # Original data preserved
        self.assertEqual(updated_record["updated_at"], "2023-01-01T13:00:00")

    def test_update_record_nonexistent(self):
        """Test updating a nonexistent record."""
        scribe = Scribe(self.grammateus)
        result = scribe.update_record(999, {"new_field": "new_value"})

        self.assertFalse(result)

    def test_transform_records_csv(self):
        """Test transforming records to CSV."""
        scribe = Scribe(self.grammateus)
        export_dir = os.path.join(self.test_dir, "exports")
        os.makedirs(export_dir, exist_ok=True)

        with patch('src.grammateus.entities.csv.DictWriter') as mock_writer_class:
            mock_writer = MagicMock()
            mock_writer_class.return_value = mock_writer

            result = scribe.transform_records("csv", export_dir)

        expected_path = os.path.join(export_dir, "records.csv")
        self.assertEqual(result, expected_path)
        mock_writer.writeheader.assert_called_once()
        self.assertEqual(mock_writer.writerow.call_count, 2)  # Called for each record

    def test_transform_records_xml(self):
        """Test transforming records to XML."""
        scribe = Scribe(self.grammateus)
        export_dir = os.path.join(self.test_dir, "exports")
        os.makedirs(export_dir, exist_ok=True)

        with patch('src.grammateus.entities.xml.dom.minidom.parseString') as mock_parse:
            mock_parsed = MagicMock()
            mock_parse.return_value = mock_parsed
            mock_parsed.toprettyxml.return_value = "<xml>Mocked XML</xml>"

            result = scribe.transform_records("xml", export_dir)

        expected_path = os.path.join(export_dir, "records.xml")
        self.assertEqual(result, expected_path)
        mock_parsed.toprettyxml.assert_called_once()

        # Check if file was created
        self.assertTrue(os.path.exists(expected_path))
        with open(expected_path, 'r') as f:
            content = f.read()
        self.assertEqual(content, "<xml>Mocked XML</xml>")

    def test_transform_records_unsupported(self):
        """Test transforming records to unsupported format."""
        scribe = Scribe(self.grammateus)
        export_dir = os.path.join(self.test_dir, "exports")

        with self.assertRaises(ValueError):
            scribe.transform_records("unsupported", export_dir)

    def test_move_records(self):
        """Test moving records to new location."""
        scribe = Scribe(self.grammateus)
        new_dir = os.path.join(self.test_dir, "new_location")

        with patch('src.grammateus.entities.shutil.copy2') as mock_copy:
            scribe.move_records(new_dir)

        # Check if directory was created
        self.assertTrue(os.path.exists(new_dir))

        # Check if copy was called
        mock_copy.assert_called_once()

        # Check if paths were updated
        self.assertEqual(scribe.grammateus.path, new_dir)
        expected_file = os.path.join(new_dir, os.path.basename(self.grammateus.records_file))
        self.assertEqual(scribe.grammateus.records_file, expected_file)

