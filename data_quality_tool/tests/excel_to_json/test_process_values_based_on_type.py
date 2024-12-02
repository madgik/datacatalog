import unittest

from common_entities import InvalidDataModelError
from converter.excel_to_json import process_values_based_on_type


class TestProcessValuesBasedOnType(unittest.TestCase):
    def test_process_integer_range(self):
        row = {"type": "integer", "values": "1-100"}
        variable = {}
        process_values_based_on_type(row, variable)
        self.assertEqual(variable["minValue"], 1)
        self.assertEqual(variable["maxValue"], 100)

    def test_process_min_max_invalid_type(self):
        row = {"type": "integer", "values": "1.1-100.1"}
        variable = {}
        with self.assertRaises(InvalidDataModelError) as context:
            process_values_based_on_type(row, variable)
        self.assertIn(
            "Range values for variable None must be valid integer numbers",
            str(context.exception),
        )

    def test_process_nominal_enumerations(self):
        row = {"type": "nominal", "values": '{"code1", "label1"}, {"code2", "label2"}'}
        variable = {}
        process_values_based_on_type(row, variable)
        expected_enumerations = [
            {"code": "code1", "label": "label1"},
            {"code": "code2", "label": "label2"},
        ]
        self.assertEqual(variable["enumerations"], expected_enumerations)

    def test_nominal_without_values_raises_error(self):
        row = {"type": "nominal", "code": "code1"}
        variable = {"code": "V1"}
        with self.assertRaises(InvalidDataModelError) as context:
            process_values_based_on_type(row, variable)
        self.assertIn(
            "The 'values' should not be empty for variable code1 when type is 'nominal'",
            str(context.exception),
        )

    def test_missing_values_for_range_raises_error(self):
        row = {"type": "real", "code": "V2"}
        variable = {}
        process_values_based_on_type(row, variable)
        self.assertNotIn("minValue", variable)
        self.assertNotIn("maxValue", variable)

    def test_integer_range_with_correct_conversion(self):
        row = {"type": "integer", "values": "1-100"}
        variable = {}
        process_values_based_on_type(row, variable)
        self.assertEqual(variable["minValue"], 1)
        self.assertEqual(variable["maxValue"], 100)
        self.assertIsInstance(variable["minValue"], int)
        self.assertIsInstance(variable["maxValue"], int)

    def test_real_range_with_correct_conversion(self):
        row = {"type": "real", "values": "0.1-99.9"}
        variable = {}
        process_values_based_on_type(row, variable)
        self.assertEqual(variable["minValue"], 0.1)
        self.assertEqual(variable["maxValue"], 99.9)
        self.assertIsInstance(variable["minValue"], float)
        self.assertIsInstance(variable["maxValue"], float)

    def test_invalid_integer_range_raises_error(self):
        row = {"type": "integer", "values": "not-an-int - 100", "code": "VInvalidInt"}
        variable = {}
        with self.assertRaises(InvalidDataModelError) as context:
            process_values_based_on_type(row, variable)
        self.assertIn(
            "Values must match format '<float or integer>-<float or integer>",
            str(context.exception),
        )

    def test_invalid_real_range_raises_error(self):
        row = {"type": "real", "values": "0.1 - not-a-real", "code": "VInvalidReal"}
        variable = {}
        with self.assertRaises(InvalidDataModelError) as context:
            process_values_based_on_type(row, variable)
        self.assertIn(
            "Values must match format '<float or integer>-<float or integer>",
            str(context.exception),
        )

    def test_invalid_type_in_values_range_raises_error(self):
        row = {"type": "real", "values": "a-b", "code": "VInvalidReal"}
        variable = {}
        with self.assertRaises(InvalidDataModelError) as context:
            process_values_based_on_type(row, variable)
        self.assertIn(
            "Values must match format '<float or integer>-<float or integer>",
            str(context.exception),
        )
