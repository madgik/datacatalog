import unittest

from converter.json_to_excel import recursive_parse_json


class TestRecursiveParseJsonFunction(unittest.TestCase):
    def test_simple_structure(self):
        json_data = {
            "code": "group1",
            "label": "Group 1",
            "variables": [{"code": "V1", "label": "Variable 1"}],
            "groups": [{"code": "subgroup1", "label": "Subgroup 1"}],
        }
        expected = [["", "Variable 1", "V1", "", "", "", "", "", "", "Group 1/V1", ""]]
        self.assertEqual(recursive_parse_json(json_data), expected)

    def test_nested_groups(self):
        json_data = {
            "groups": [
                {
                    "code": "group1",
                    "label": "Group 1",
                    "groups": [
                        {
                            "code": "subgroup1",
                            "label": "Subgroup 1",
                            "variables": [{"code": "V1", "label": "Variable 1"}],
                        }
                    ],
                }
            ]
        }
        expected = [
            [
                "",
                "Variable 1",
                "V1",
                "",
                "",
                "",
                "",
                "",
                "",
                "Group 1/Subgroup 1/V1",
                "",
            ]
        ]
        self.assertEqual(recursive_parse_json(json_data), expected)

    def test_empty_json_data(self):
        self.assertEqual(recursive_parse_json({}), [])
        self.assertEqual(recursive_parse_json([]), [])

    def test_variables_at_multiple_levels(self):
        json_data = {
            "code": "root",
            "variables": [{"code": "VR", "label": "Variable Root"}],
            "groups": [
                {
                    "code": "group1",
                    "variables": [{"code": "V1", "label": "Variable 1"}],
                    "groups": [
                        {
                            "code": "subgroup1",
                            "variables": [{"code": "V2", "label": "Variable 2"}],
                        }
                    ],
                }
            ],
        }
        expected = [
            ["", "Variable Root", "VR", "", "", "", "", "", "", "root/VR", ""],
            ["", "Variable 1", "V1", "", "", "", "", "", "", "root/group1/V1", ""],
            [
                "",
                "Variable 2",
                "V2",
                "",
                "",
                "",
                "",
                "",
                "",
                "root/group1/subgroup1/V2",
                "",
            ],
        ]
        self.assertEqual(recursive_parse_json(json_data), expected)

    def test_groups_without_variables(self):
        json_data = {
            "groups": [
                {
                    "code": "group1",
                    "label": "Group 1",
                    "groups": [
                        {
                            "code": "subgroup1",
                            "label": "Subgroup 1",
                            "groups": [
                                {"code": "subsubgroup1", "label": "Sub-Subgroup 1"}
                            ],  # No variables
                        }
                    ],
                }
            ]
        }
        self.assertEqual(recursive_parse_json(json_data), [])

    def test_invalid_json_structure(self):
        json_data = {"unexpected_key": "unexpected_value"}
        # Depending on how you choose to handle invalid structures, adjust the expected outcome
        self.assertEqual(recursive_parse_json(json_data), [])

    def test_special_characters_in_codes_and_labels(self):
        json_data = {
            "code": "group$1",
            "label": "Group &1",
            "variables": [{"code": "V@1", "label": "Variable *1"}],
        }
        expected = [
            ["", "Variable *1", "V@1", "", "", "", "", "", "", "Group &1/V@1", ""]
        ]
        self.assertEqual(recursive_parse_json(json_data), expected)
