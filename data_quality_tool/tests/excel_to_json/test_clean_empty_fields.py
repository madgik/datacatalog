import unittest

from converter.excel_to_json import clean_empty_fields


class TestCleanEmptyFields(unittest.TestCase):
    def test_remove_empty_lists_and_strings(self):
        data = {
            "uuid": "some-uuid",
            "label": "",
            "variables": [],
            "groups": [
                {
                    "code": "Example Group",
                    "label": "Example Group",
                    "variables": [
                        {
                            "code": "group_variable",
                            "label": "Group Variable",
                            "description": "",
                            "enumerations": [],
                            "type": "integer",
                        }
                    ],
                    "groups": [],
                }
            ],
        }
        expected = {
            "uuid": "some-uuid",
            "groups": [
                {
                    "code": "Example Group",
                    "label": "Example Group",
                    "variables": [
                        {
                            "code": "group_variable",
                            "label": "Group Variable",
                            "type": "integer",
                        }
                    ],
                }
            ],
        }
        clean_empty_fields(data)
        self.assertEqual(data, expected)

    def test_no_change_needed(self):
        data = {
            "uuid": "some-uuid",
            "code": "example",
            "variables": [
                {
                    "code": "dataset",
                    "label": "Dataset Variable",
                    "type": "nominal",
                }
            ],
            "groups": [
                {
                    "code": "Example Group",
                    "label": "Example Group",
                }
            ],
        }
        expected = data.copy()  # Make a copy of data as no change is expected
        clean_empty_fields(data)
        self.assertEqual(data, expected)

    def test_nested_empty_fields(self):
        data = {
            "uuid": "some-uuid",
            "groups": [
                {
                    "code": "",
                    "groups": [{"code": "Nested Group", "variables": [], "groups": []}],
                    "variables": [],
                }
            ],
        }
        expected = {
            "uuid": "some-uuid",
            "groups": [
                {
                    "groups": [
                        {
                            "code": "Nested Group",
                        }
                    ],
                }
            ],
        }
        clean_empty_fields(data)
        self.assertEqual(data, expected)
