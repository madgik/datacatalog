import unittest
import json
from urllib.parse import quote

import pandas as pd

from common_entities import InvalidDataModelError
from converter.excel_to_json import convert_excel_to_json
from converter.json_to_excel import ROOT_METADATA_CODE, ROOT_METADATA_PREFIX


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
            convert_excel_to_json(df)

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

    def test_metadata_code_collision_variable_is_not_dropped(self):
        metadata_payload = {
            "code": "DM",
            "label": "DM",
            "version": "1.0",
        }
        metadata_row = {
            "csvFile": ROOT_METADATA_PREFIX
            + quote(json.dumps(metadata_payload, separators=(",", ":")), safe=""),
            "name": ROOT_METADATA_CODE,
            "code": ROOT_METADATA_CODE,
            "type": "text",
            "values": "",
            "unit": "",
            "description": "",
            "canBeNull": "",
            "comments": "",
            "conceptPath": f"{ROOT_METADATA_CODE}/{ROOT_METADATA_CODE}",
            "methodology": "",
        }
        data_row_with_same_code = {
            "csvFile": "",
            "name": "Sentinel Variable",
            "code": ROOT_METADATA_CODE,
            "type": "text",
            "values": "",
            "unit": "",
            "description": "",
            "canBeNull": "",
            "comments": "",
            "conceptPath": f"DM/{ROOT_METADATA_CODE}",
            "methodology": "",
        }
        df = pd.DataFrame([metadata_row, data_row_with_same_code])

        result = convert_excel_to_json(df)

        self.assertEqual(result["code"], "DM")
        self.assertEqual(len(result["variables"]), 1)
        self.assertEqual(result["variables"][0]["code"], ROOT_METADATA_CODE)

    def test_multiple_metadata_rows_raise_error(self):
        metadata_payload = {
            "code": "DM",
            "label": "DM",
            "version": "1.0",
        }
        row = {
            "csvFile": ROOT_METADATA_PREFIX
            + quote(json.dumps(metadata_payload, separators=(",", ":")), safe=""),
            "name": ROOT_METADATA_CODE,
            "code": ROOT_METADATA_CODE,
            "type": "text",
            "values": "",
            "unit": "",
            "description": "",
            "canBeNull": "",
            "comments": "",
            "conceptPath": f"{ROOT_METADATA_CODE}/{ROOT_METADATA_CODE}",
            "methodology": "",
        }
        df = pd.DataFrame([row, row])

        with self.assertRaisesRegex(
            InvalidDataModelError, "Multiple root metadata rows found"
        ):
            convert_excel_to_json(df)

    def test_invalid_metadata_payload_raises_error(self):
        invalid_metadata_row = {
            "csvFile": ROOT_METADATA_PREFIX + "not-json",
            "name": ROOT_METADATA_CODE,
            "code": ROOT_METADATA_CODE,
            "type": "text",
            "values": "",
            "unit": "",
            "description": "",
            "canBeNull": "",
            "comments": "",
            "conceptPath": f"{ROOT_METADATA_CODE}/{ROOT_METADATA_CODE}",
            "methodology": "",
        }
        df = pd.DataFrame([invalid_metadata_row])

        with self.assertRaisesRegex(
            InvalidDataModelError, "Invalid root metadata row in Excel input"
        ):
            convert_excel_to_json(df)

    def test_non_object_metadata_payload_raises_error(self):
        metadata_row = {
            "csvFile": ROOT_METADATA_PREFIX
            + quote(json.dumps([1], separators=(",", ":")), safe=""),
            "name": ROOT_METADATA_CODE,
            "code": ROOT_METADATA_CODE,
            "type": "text",
            "values": "",
            "unit": "",
            "description": "",
            "canBeNull": "",
            "comments": "",
            "conceptPath": f"{ROOT_METADATA_CODE}/{ROOT_METADATA_CODE}",
            "methodology": "",
        }
        df = pd.DataFrame([metadata_row])

        with self.assertRaisesRegex(
            InvalidDataModelError, "Invalid root metadata row in Excel input"
        ):
            convert_excel_to_json(df)
