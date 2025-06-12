import json
import unittest
from io import BytesIO

import pandas as pd

from data_quality_tool.common_entities import EXCEL_COLUMNS
from controller import app


class TestController(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.testing = True
        self.client = self.app.test_client()

    def test_excel_to_json_conversion(self):
        with open("MinimalDataModelExample.xlsx", "rb") as file:
            data = {"file": (file, "MinimalDataModelExample.xlsx")}
            response = self.client.post(
                "/excel-to-json", content_type="multipart/form-data", data=data
            )
            self.assertEqual(response.status_code, 200)
            minimal_data_model = json.loads(response.data.decode())
            print(minimal_data_model)

            # Expected minimal data model JSON
            expected_data_model = {
                "code": "Minimal Example",
                "label": "Minimal Example",
                "groups": [
                    {
                        "code": "Example Group",
                        "label": "Example Group",
                        "groups": [
                            {
                                "code": "Nested Group",
                                "label": "Nested Group",
                                "variables": [
                                    {
                                        "label": "Nested Group Variable",
                                        "code": "nested_group_variable",
                                        "type": "nominal",
                                        "description": "A nested group variable",
                                        "methodology": "nested methodology",
                                        "enumerations": [
                                            {
                                                "code": "nested_enum1",
                                                "label": "Nested Enumeration 1",
                                            }
                                        ],
                                        "sql_type": "text",
                                        "isCategorical": True,
                                    }
                                ],
                            }
                        ],
                        "variables": [
                            {
                                "label": "Group Variable",
                                "code": "group_variable",
                                "type": "integer",
                                "units": "years",
                                "description": "A variable within a group",
                                "methodology": "group methodology",
                                "minValue": 0,
                                "maxValue": 100,
                                "sql_type": "int",
                                "isCategorical": False,
                            }
                        ],
                    }
                ],
                "variables": [
                    {
                        "label": "Dataset Variable",
                        "code": "dataset",
                        "type": "nominal",
                        "units": "unit",
                        "description": "An example variable description",
                        "methodology": "example methodology",
                        "enumerations": [{"code": "enum1", "label": "Enumeration 1"}],
                        "sql_type": "text",
                        "isCategorical": True,
                    }
                ],
                "version": "to be defined",
            }

            # Assert that the actual data model matches the expected data model
            self.assertEqual(minimal_data_model, expected_data_model)

    def test_json_to_excel_conversion(self):
        with open("MinimalDataModelExample.json", "r") as file:
            json_data = json.load(file)
        response = self.client.post(
            "/json-to-excel", json=json_data, content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.content_type,
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

        # Read the Excel file from the response
        excel_file = BytesIO(response.data)
        df = pd.read_excel(excel_file)

        self.assertSetEqual(set(df.columns), set(EXCEL_COLUMNS))
        self.assertEqual(
            df["name"].tolist(),
            ["Dataset Variable", "Group Variable", "Nested Group Variable"],
        )

        self.assertEqual(
            df["code"].tolist(), ["dataset", "group_variable", "nested_group_variable"]
        )
        self.assertEqual(df["type"].tolist(), ["nominal", "integer", "nominal"])
        self.assertEqual(
            df["values"].tolist(),
            [
                '{"enum1","Enumeration 1"}',
                "0-100",
                '{"nested_enum1","Nested Enumeration 1"}',
            ],
        )
        self.assertEqual(
            df["conceptPath"].tolist(),
            [
                "Minimal Example/dataset",
                "Minimal Example/Example Group/group_variable",
                "Minimal Example/Example Group/Nested Group/nested_group_variable",
            ],
        )
        self.assertEqual(
            df["methodology"].tolist(),
            ["example methodology", "group methodology", "nested methodology"],
        )

    def test_excel_to_json_conversion_no_excel(self):
        response = self.client.post(
            "/excel-to-json", content_type="multipart/form-data", data={}
        )
        self.assertEqual(response.status_code, 400)

    def test_json_to_excel_conversion_no_json(self):
        response = self.client.post(
            "/json-to-excel", json="", content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)

    def test_excel_to_json_no_selected_file(self):
        # Simulate sending a file with an empty filename
        data = {"file": (BytesIO(), "")}  # Empty filename
        response = self.client.post(
            "/excel-to-json", content_type="multipart/form-data", data=data
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {"error": "No selected file"})

    def test_validate_json_success(self):
        with open("MinimalDataModelExample.json", "r") as file:
            json_data = json.load(file)

        response = self.client.post(
            "/validate-json", json=json_data, content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)

        response_data = response.json
        self.assertIn("message", response_data)
        self.assertEqual(response_data["message"], "Data model is valid.")

    def test_validate_json_invalid_structure(self):
        with open("MinimalDataModelExample.json", "r") as file:
            json_data = json.load(file)

        del json_data["code"]
        response = self.client.post(
            "/validate-json", json=json_data, content_type="application/json"
        )

        self.assertEqual(response.status_code, 400)

        response_data = response.json
        self.assertIn("error", response_data)
        self.assertEqual(
            "DataModel is missing the required field 'code'. Please include it in the input JSON.",
            response_data["error"],
        )

    def test_validate_json_no_json(self):
        response = self.client.post(
            "/validate-json", json="", content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)

    def test_validate_excel_success(self):
        with open("MinimalDataModelExample.xlsx", "rb") as file:
            data = {"file": (file, "MinimalDataModelExample.xlsx")}
            response = self.client.post(
                "/validate-excel", content_type="multipart/form-data", data=data
            )
            self.assertEqual(response.status_code, 200)

            response_data = response.json
            self.assertIn("message", response_data)
            self.assertEqual(response_data["message"], "Data model is valid.")

    def test_validate_excel_no_excel(self):
        response = self.client.post(
            "/validate-excel", content_type="multipart/form-data", data={}
        )
        self.assertEqual(response.status_code, 400)

    def test_validate_excel_no_selected_file(self):
        # Simulate sending a file with an empty filename
        data = {"file": (BytesIO(), "")}  # Empty filename
        response = self.client.post(
            "/validate-excel", content_type="multipart/form-data", data=data
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {"error": "No selected file"})

    def test_validate_excel_missing_column(self):
        with open("MinimalDataModelError.xlsx", "rb") as file:
            data = {"file": (file, "MinimalDataModelExample.xlsx")}
            response = self.client.post(
                "/validate-excel", content_type="multipart/form-data", data=data
            )
            self.assertEqual(response.status_code, 400)

            response_data = response.json
            self.assertIn("error", response_data)
            self.assertEqual(
                "On :dataset got: Missing value for required column 'name'.",
                response_data["error"],
            )
