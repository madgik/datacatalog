import unittest

from common_entities import InvalidDataModelError
from converter.json_to_excel import extract_values


class TestExtractValuesFunction(unittest.TestCase):
    def test_with_enumerations(self):
        variable = {
            "enumerations": [
                {"code": "C1", "label": "Label 1"},
                {"code": "C2", "label": "Label 2"},
            ]
        }
        expected = '{"C1","Label 1"},{"C2","Label 2"}'
        self.assertEqual(extract_values(variable), expected)

    def test_with_min_max_values(self):
        variable = {"minValue": "1", "maxValue": "10"}
        expected = "1-10"
        self.assertEqual(extract_values(variable), expected)

    def test_with_min_value_only(self):
        variable = {"minValue": "1"}
        expected = "1-"
        self.assertEqual(extract_values(variable), expected)

    def test_with_max_value_only(self):
        variable = {"maxValue": "100"}
        expected = "-100"
        self.assertEqual(extract_values(variable), expected)

    def test_with_no_values(self):
        variable = {}
        expected = ""
        self.assertEqual(extract_values(variable), expected)

    def test_with_enumerations_special_chars(self):
        variable = {
            "enumerations": [
                {"code": "C1!", "label": "Label 1&"},
                {"code": "C2@", "label": "Label 2*"},
            ]
        }
        expected = '{"C1!","Label 1&"},{"C2@","Label 2*"}'
        self.assertEqual(extract_values(variable), expected)

    def test_with_numeric_min_max_values(self):
        variable = {"minValue": 0, "maxValue": 100}
        expected = "0-100"
        self.assertEqual(extract_values(variable), expected)

    def test_enumerations_missing_code_raises_error(self):
        variable = {"enumerations": [{"label": "Only Label"}]}  # Missing 'code'
        with self.assertRaises(InvalidDataModelError):
            extract_values(variable)

    def test_enumerations_missing_label_raises_error(self):
        variable = {"enumerations": [{"code": "OnlyCode"}]}  # Missing 'label'
        with self.assertRaises(InvalidDataModelError):
            extract_values(variable)

    def test_enumerations_with_special_characters_escaping(self):
        variable = {
            "enumerations": [
                {"code": 'C1"special"', "label": 'Label 1"special"'},
                {"code": "C2'special", "label": "Label 2'special"},
            ]
        }
        expected = '{"C1\\"special\\"","Label 1\\"special\\""},{"C2\'special","Label 2\'special"}'
        result = extract_values(variable)
        self.assertEqual(result, expected)
