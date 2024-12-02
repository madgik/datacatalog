import unittest

import pandas as pd

from common_entities import InvalidDataModelError
from converter.excel_to_json import convert_excel_to_json


class TestConvertExcelToJson(unittest.TestCase):
    def setUp(self):
        # Basic setup for DataFrame used in multiple tests
        self.data = {
            "type": ["nominal", "integer"],
            "values": ['{"code1", "label1"}, {"code2", "label2"}', "1-100"],
            "name": ["Nominal Variable", "Integer Variable"],
            "code": ["NomVar", "IntVar"],
            "conceptPath": ["Group1/NomVar", "Group1/IntVar"],
        }
        self.df = pd.DataFrame(self.data)

    def test_successful_conversion(self):
        expected_output = {
            "code": "Group1",
            "label": "Group1",
            "groups": [],
            "variables": [
                # Expected processed variables
            ],
            "version": "to be defined",
        }
        result = convert_excel_to_json(self.df)
        self.assertEqual(result["code"], expected_output["code"])
        self.assertEqual(result["version"], "to be defined")

    def test_missing_conceptPath_raises_error(self):
        data_with_missing_path = {
            "type": ["nominal"],
            "values": ['{"code1", "label1"}'],
            "name": ["Nominal Variable Missing Path"],
            "code": ["NomVarMissingPath"],
            # Missing conceptPath
        }
        df_missing_path = pd.DataFrame(data_with_missing_path)
        with self.assertRaises(InvalidDataModelError) as context:
            convert_excel_to_json(df_missing_path)
        self.assertIn("missing the conceptPath", str(context.exception))

    def test_empty_dataframe(self):
        df_empty = pd.DataFrame()
        result = convert_excel_to_json(df_empty)
        self.assertEqual(
            result, {"code": "No groups found", "groups": [], "variables": []}
        )

    def test_partially_missing_data(self):
        # Scenario where some rows have missing 'conceptPath' or other critical fields
        data = {
            "type": ["nominal", "integer", "text"],
            "values": [
                '{"code1", "label1"}',
                "1-100",
                None,
            ],  # Text type usually doesn't have 'values'
            "name": ["Variable 1", "Variable 2", "Variable 3"],
            "code": ["Var1", "Var2", "Var3"],
            "conceptPath": [
                "Group1/Var1",
                None,
                "Group2/Var3",
            ],  # Missing conceptPath for Var2
        }
        df = pd.DataFrame(data)

        expected_message = (
            "Error processing variable: The variable Var2 is missing the conceptPath"
        )
        with self.assertRaisesRegex(InvalidDataModelError, expected_message):
            print(convert_excel_to_json(df))

    def test_deeply_nested_conceptPath(self):
        # Scenario with a deeply nested conceptPath
        data = {
            "type": ["nominal"],
            "values": ['{"code1", "label1"}'],
            "name": ["Deeply Nested Variable"],
            "code": ["DeepVar"],
            "conceptPath": ["Group1/Subgroup1/Subsubgroup1/DeepVar"],
        }
        df = pd.DataFrame(data)
        result = convert_excel_to_json(df)
        # Check if the deeply nested structure is correctly formed
        self.assertEqual(len(result["groups"]), 1)
        self.assertEqual(result["groups"][0]["code"], "Subgroup1")

        self.assertEqual(len(result["groups"][0]["groups"]), 1)  # Subgroup1
        self.assertEqual(
            result["groups"][0]["groups"][0]["code"], "Subsubgroup1"
        )  # Subgroup1
        self.assertEqual(
            len(result["groups"][0]["groups"][0]["variables"]), 1
        )  # Subsubgroup1
        self.assertEqual(
            result["groups"][0]["groups"][0]["variables"][0]["code"], "DeepVar"
        )

    def test_dataframe_with_invalid_type_raises_error(self):
        # Scenario where a row has an invalid 'type' that fails validation
        data = {
            "type": ["invalid_type"],
            "values": ["1-100"],
            "name": ["Invalid Type Variable"],
            "code": ["InvalidTypeVar"],
            "conceptPath": ["Group1/InvalidTypeVar"],
        }
        df = pd.DataFrame(data)

        with self.assertRaises(InvalidDataModelError) as context:
            convert_excel_to_json(df)
        self.assertIn(
            "The row must have a 'type' field with a valid value",
            str(context.exception),
        )

    def test_variables_without_group_nesting(self):
        # Variables that should be placed directly under the root due to lack of conceptPath or other logic
        data = {
            "type": ["text", "real"],
            "values": [None, "0.1-100.0"],
            "name": ["Ungrouped Text Variable", "Ungrouped Real Variable"],
            "code": ["UngroupedTextVar", "UngroupedRealVar"],
            "conceptPath": [
                None,
                None,
            ],  # Intentionally missing to simulate ungrouped variables
        }
        df = pd.DataFrame(data)
        expected_message = "The variable UngroupedTextVar is missing the conceptPath"
        with self.assertRaisesRegex(InvalidDataModelError, expected_message):
            convert_excel_to_json(df)
