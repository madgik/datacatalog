import unittest

from common_entities import InvalidDataModelError
from converter.excel_to_json import process_variable


class TestProcessVariable(unittest.TestCase):
    def test_process_nominal_variable(self):
        row = {
            "type": "nominal",
            "values": '{"code1", "label1"}, {"code2", "label2"}',
            "name": "Variable Name",
            "code": "VarCode",
        }
        expected_variable = {
            "label": "Variable Name",
            "code": "VarCode",
            "type": "nominal",
            "enumerations": [
                {"code": "code1", "label": "label1"},
                {"code": "code2", "label": "label2"},
            ],
            "isCategorical": True,
            "sql_type": "text",
        }
        result_variable = process_variable(row)
        self.assertEqual(result_variable, expected_variable)

    def test_process_integer_variable(self):
        row = {
            "type": "integer",
            "values": "1-100",
            "name": "Integer Variable",
            "code": "IntVar",
        }
        expected_variable = {
            "label": "Integer Variable",
            "code": "IntVar",
            "type": "integer",
            "minValue": 1,
            "maxValue": 100,
            "isCategorical": False,
            "sql_type": "int",
        }
        result_variable = process_variable(row)
        self.assertEqual(result_variable, expected_variable)

    def test_invalid_type_raises_error(self):
        row = {
            "type": "undefined",
            "name": "Invalid Type Variable",
            "code": "InvalidTypeVar",
        }
        with self.assertRaises(InvalidDataModelError):
            process_variable(row)

    def test_process_real_variable_with_range(self):
        row = {
            "type": "real",
            "values": "0.01-99.99",
            "name": "Real Variable",
            "code": "RealVar",
            "description": "A real number variable",
        }
        expected_variable = {
            "label": "Real Variable",
            "code": "RealVar",
            "type": "real",
            "minValue": 0.01,
            "maxValue": 99.99,
            "description": "A real number variable",
            "isCategorical": False,
            "sql_type": "real",
        }
        result_variable = process_variable(row)
        self.assertEqual(result_variable, expected_variable)

    def test_process_text_variable(self):
        row = {
            "type": "text",
            "name": "Text Variable",
            "code": "TextVar",
            "description": "A text variable",
        }
        expected_variable = {
            "label": "Text Variable",
            "code": "TextVar",
            "type": "text",
            "description": "A text variable",
            "isCategorical": False,
            "sql_type": "text",
        }
        result_variable = process_variable(row)
        self.assertEqual(result_variable, expected_variable)

    def test_variable_with_missing_values_field(self):
        row = {"type": "nominal", "name": "Nominal Variable", "code": "NominalVar"}
        with self.assertRaises(InvalidDataModelError) as context:
            process_variable(row)
        self.assertIn(
            "The 'values' should not be empty for variable NominalVar when type is 'nominal'",
            str(context.exception),
        )

    def test_variable_with_optional_fields_missing(self):
        row = {"type": "integer", "values": "1-100", "code": "IntVar"}
        expected_variable = {
            "code": "IntVar",
            "type": "integer",
            "minValue": 1,
            "maxValue": 100,
            "isCategorical": False,
            "sql_type": "int",
        }
        result_variable = process_variable(row)
        self.assertEqual(result_variable, expected_variable)
        self.assertNotIn("label", result_variable)

    def test_process_variable_with_additional_fields(self):
        row = {
            "type": "real",
            "values": "10.5-20.5",
            "name": "Additional Field Variable",
            "code": "AddFieldVar",
            "additional": "Extra info",
        }
        expected_variable = {
            "label": "Additional Field Variable",
            "code": "AddFieldVar",
            "type": "real",
            "minValue": 10.5,
            "maxValue": 20.5,
            "isCategorical": False,
            "sql_type": "real",
        }
        result_variable = process_variable(row)
        self.assertEqual(result_variable, expected_variable)
        self.assertNotIn("additional", result_variable)

    def test_nominal_with_range_instead_of_enumerations(self):
        row = {
            "type": "nominal",
            "values": "1-100",
            "name": "Incorrect Nominal Variable",
            "code": "IncorrNomVar",
        }
        with self.assertRaises(InvalidDataModelError) as context:
            process_variable(row)
        self.assertEqual(
            """Nominal values format error: '{"code", "label"}, {"code", "label"}' expected but got 1-100.""",
            str(context.exception),
        )
