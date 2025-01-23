import unittest

import pandas as pd

from common_entities import REQUIRED_COLUMNS, EXCEL_COLUMNS
from validator.excel_validator import (
    validate_enumerations,
    InvalidDataModelError,
    validate_min_max,
    validate_concept_path,
    validate_variable,
    validate_excel,
)


class TestValidationFunctions(unittest.TestCase):
    def test_validate_enumeration_valid(self):
        validate_enumerations('{"code1", "label1"}, {"code2", "label2"}')

    def test_validate_enumeration_invalid(self):
        with self.assertRaises(InvalidDataModelError) as context:
            validate_enumerations("Invalid format")
        self.assertEqual(
            (
                'Nominal values format error: \'{"code", "label"}, {"code", "label"}\' '
                "expected but got Invalid format."
            ),
            str(context.exception),
        )

    def test_validate_min_max_valid(self):
        self.assertIsNone(validate_min_max("1-2"))

    def test_validate_min_max_invalid_format(self):
        with self.assertRaises(InvalidDataModelError) as context:
            validate_min_max("Invalid format")
        self.assertEqual(
            "Values must match format '<float or integer>-<float or integer>' but got 'Invalid format'.",
            str(context.exception),
        )

    def test_validate_min_max_invalid_logic(self):
        with self.assertRaises(InvalidDataModelError) as context:
            validate_min_max("2-1")
        self.assertEqual(
            "Min value must be smaller than max value min_value='2' and max_value='1'.",
            str(context.exception),
        )

    def test_validate_conceptPath_valid(self):
        self.assertIsNone(validate_concept_path("valid/format/here"))

    def test_validate_conceptPath_invalid(self):
        with self.assertRaises(InvalidDataModelError) as context:
            validate_concept_path("invalid//format")
        self.assertEqual(
            "ConceptPath format error: 'characters/characters/...' expected.",
            str(context.exception),
        )

    def test_validate_variable_missing_required_columns(self):
        row = {"name": "test", "code": "T01", "type": "nominal", "conceptPath": None}
        with self.assertRaises(InvalidDataModelError) as context:
            validate_variable(row)
        self.assertTrue("Missing value for required column" in str(context.exception))

    def test_validate_variable_with_min_max(self):
        row = {
            "name": "test",
            "code": "T01",
            "type": "integer",
            "conceptPath": "valid/format",
            "values": "10-100",
        }
        validate_variable(row)

    def test_validate_variable_invalid_type(self):
        row = {
            "name": "test",
            "code": "T01",
            "type": "invalid",
            "conceptPath": "valid/format",
        }
        with self.assertRaises(InvalidDataModelError) as context:
            validate_variable(row)
        self.assertTrue("Invalid 'type'" in str(context.exception))

    def test_validate_excel_valid(self):
        df = pd.DataFrame(
            [
                {
                    "csvFile": "csvFile",
                    "name": "test1",
                    "code": "T01",
                    "type": "nominal",
                    "values": '{"code1", "label1"}, {"code2", "label2"}',
                    "units": "",
                    "description": "",
                    "canBeNull": "",
                    "comments": "",
                    "conceptPath": "valid/format",
                    "methodology": "methodology",
                }
            ],
            columns=EXCEL_COLUMNS,
        )
        validate_excel(df)

    def test_validate_excel_invalid_columns(self):
        df = pd.DataFrame(
            [
                {
                    "name": "test2",
                    "code": "T02",
                    "type": "nominal",
                    "conceptPath": "valid/format",
                }
            ]
        )  # Missing required columns
        with self.assertRaises(InvalidDataModelError) as context:
            validate_excel(df)
        self.assertIn(
            "Mismatch in Excel columns. Missing columns",
            str(context.exception),
        )

    def test_valid_enumeration(self):
        """Test that a valid enumeration does not raise an error."""
        valid_values = '{"code1", "label1"}, {"code2", "label2"}'
        validate_enumerations(valid_values)

    def test_valid_enumeration_with_spaces(self):
        """Test that a valid enumeration does not raise an error."""
        valid_values = '{"code1","label1"},{"code2","label2"}'
        validate_enumerations(valid_values)

    def test_invalid_format_enumeration(self):
        """Test that an invalid format raises the correct error."""
        invalid_values = "Invalid format"
        with self.assertRaises(InvalidDataModelError) as context:
            validate_enumerations(invalid_values)
        self.assertIn("Nominal values format error", str(context.exception))

    def test_duplicate_codes_enumeration(self):
        """Test that duplicate codes raise the correct error."""
        duplicate_values = '{"code1", "label1"}, {"code1", "label2"}'
        with self.assertRaises(InvalidDataModelError) as context:
            validate_enumerations(duplicate_values)
        self.assertIn("Duplicate codes found", str(context.exception))
