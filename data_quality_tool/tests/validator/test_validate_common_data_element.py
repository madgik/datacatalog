import unittest

from validator.json_validator import validate_common_data_element, InvalidDataModelError


class TestValidateCommonDataElement(unittest.TestCase):
    def test_valid_common_data_element_nominal(self):
        # Test a valid nominal common data element with enumerations
        cde = {
            "code": "001",
            "sql_type": "text",
            "isCategorical": True,
            "type": "nominal",
            "enumerations": ["value1", "value2"],
        }
        path = "/test/nominal"
        # Should not raise an exception
        validate_common_data_element(cde, path)

    def test_missing_required_fields(self):
        # Test CDE missing one or more required fields
        cde_incomplete = {"code": "002", "type": "real"}
        path = "/test/missing_fields"
        with self.assertRaises(InvalidDataModelError):
            validate_common_data_element(cde_incomplete, path)

    def test_invalid_type(self):
        # Test CDE with an invalid type
        cde_invalid_type = {
            "code": "003",
            "sql_type": "text",
            "isCategorical": False,
            "type": "undefined_type",
        }
        path = "/test/invalid_type"
        with self.assertRaises(InvalidDataModelError):
            validate_common_data_element(cde_invalid_type, path)

    def test_mismatch_sql_type_and_isCategorical(self):
        # Test CDE where sql_type or isCategorical does not match the expected values for the type
        cde_mismatch = {
            "code": "004",
            "sql_type": "int",  # Expected to be 'text' for 'nominal'
            "isCategorical": True,
            "type": "nominal",
        }
        path = "/test/mismatch"
        with self.assertRaises(InvalidDataModelError):
            validate_common_data_element(cde_mismatch, path)

    def test_categorical_without_enumerations(self):
        # Test CDE that is categorical but missing enumerations
        cde_no_enumerations = {
            "code": "005",
            "sql_type": "text",
            "isCategorical": True,
            "type": "nominal",
        }
        path = "/test/no_enumerations"
        with self.assertRaises(InvalidDataModelError):
            validate_common_data_element(cde_no_enumerations, path)

    def test_minValue_greater_than_maxValue(self):
        # Test CDE with minValue greater than maxValue
        cde_invalid_range = {
            "code": "006",
            "sql_type": "real",
            "isCategorical": False,
            "type": "real",
            "minValue": 10,
            "maxValue": 5,
        }
        path = "/test/invalid_range"
        with self.assertRaises(InvalidDataModelError):
            validate_common_data_element(cde_invalid_range, path)
