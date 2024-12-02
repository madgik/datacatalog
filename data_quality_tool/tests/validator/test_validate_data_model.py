import unittest

from validator.json_validator import InvalidDataModelError, validate_json


class TestValidateDataModel(unittest.TestCase):
    def test_valid_data_model(self):
        # Test a fully valid data model
        data_model = {
            "code": "DM001",
            "version": "1.0",
            "label": "Test Data Model",
            "variables": [
                {
                    "code": "dataset",
                    "sql_type": "text",
                    "isCategorical": True,
                    "type": "nominal",
                    "enumerations": ["dataset1", "dataset2"],
                }
            ],
            "groups": [
                {
                    "code": "group",
                    "variables": [
                        {
                            "code": "001",
                            "sql_type": "text",
                            "isCategorical": True,
                            "type": "nominal",
                            "enumerations": ["yes", "no"],
                        }
                    ],
                    "groups": [
                        {
                            "code": "group",
                            "variables": [
                                {
                                    "code": "002",
                                    "sql_type": "text",
                                    "isCategorical": True,
                                    "type": "nominal",
                                    "enumerations": ["yes", "no"],
                                }
                            ],
                            "groups": [],
                        }],
                }
            ],
        }
        validate_json(data_model)

    def test_data_model_missing_required_fields(self):
        # Ensuring meaningful error messages for missing required fields
        data_model_incomplete = {
            "code": "DM002",
            "label": "Incomplete Data Model",
            # Missing 'version', 'variables', and 'groups'
        }
        expected_message = "Missing 'version' in DataModel"
        with self.assertRaisesRegex(InvalidDataModelError, expected_message):
            validate_json(data_model_incomplete)

    def test_data_model_required_field_empty_value(self):
        # Test a fully valid data model
        data_model = {
            "code": "",
            "version": "1.0",
            "label": "Test Data Model",
            "variables": [],
            "groups": [],
        }
        expected_message = "'code' in DataModel must be a non-empty string"
        with self.assertRaisesRegex(InvalidDataModelError, expected_message):
            validate_json(data_model)

    def test_data_model_without_required_dataset(self):
        # Data model lacking the required 'dataset' CommonDataElement
        data_model_no_dataset = {
            "code": "DM003",
            "version": "1.0",
            "label": "No Dataset Data Model",
            "variables": [
                {
                    "code": "000",
                    "sql_type": "text",
                    "isCategorical": True,
                    "type": "nominal",
                    "enumerations": ["yes", "no"],
                }
            ],
            "groups": [
                {
                    "code": "group",
                    "variables": [
                        {
                            "code": "001",
                            "sql_type": "text",
                            "isCategorical": True,
                            "type": "nominal",
                            "enumerations": ["yes", "no"],
                        }
                    ],
                    "groups": [],
                }
            ],
        }
        expected_message = (
            "The data model must always contain a dataset CommonDataElement"
        )
        with self.assertRaisesRegex(InvalidDataModelError, expected_message):
            validate_json(data_model_no_dataset)

    def test_valid_longitudinal_data_model(self):
        # Test a valid longitudinal data model including 'subjectid' and 'visitid'
        data_model_longitudinal = {
            "code": "DM005",
            "version": "1.0",
            "label": "Longitudinal Data Model",
            "variables": [
                {
                    "code": "dataset",
                    "sql_type": "text",
                    "isCategorical": True,
                    "type": "nominal",
                    "enumerations": ["dataset1", "dataset2"],
                },
                {
                    "code": "subjectid",
                    "sql_type": "text",
                    "isCategorical": False,
                    "type": "text",
                },
                {
                    "code": "visitid",
                    "sql_type": "text",
                    "isCategorical": False,
                    "type": "text",
                },
            ],
            "groups": [
                {
                    "code": "group",
                    "variables": [
                        {
                            "code": "001",
                            "sql_type": "text",
                            "isCategorical": True,
                            "type": "nominal",
                            "enumerations": ["yes", "no"],
                        }
                    ],
                    "groups": [],
                }
            ],
            "longitudinal": True,
        }
        validate_json(data_model_longitudinal)

    def test_data_model_with_invalid_variables(self):
        # Test a data model with variables having incorrect configurations
        data_model = {
            "code": "DM006",
            "version": "1.0",
            "label": "Data Model with Invalid Variables",
            "variables": [
                {
                    "code": "invalid_var",
                    "sql_type": "text",
                }  # Missing 'isCategorical' and 'type'
            ],
            "groups": [
                {
                    "code": "group",
                    "variables": [
                        {
                            "code": "001",
                            "sql_type": "text",
                            "isCategorical": True,
                            "type": "nominal",
                            "enumerations": ["yes", "no"],
                        }
                    ],
                    "groups": [],
                }
            ],
        }
        expected_message = (
            "Missing 'isCategorical' in CommonDataElement at '/DM006/invalid_var'"
        )
        with self.assertRaisesRegex(InvalidDataModelError, expected_message):
            validate_json(data_model)

    def test_longitudinal_data_model_missing_required_variables(self):
        # Test longitudinal data models missing 'subjectid' or 'visitid'
        data_model_missing_subjectid = {
            "code": "DM007",
            "version": "1.0",
            "label": "Missing SubjectID",
            "variables": [
                {
                    "code": "dataset",
                    "sql_type": "text",
                    "isCategorical": True,
                    "type": "nominal",
                    "enumerations": ["dataset1"],
                },
                {
                    "code": "visitid",
                    "sql_type": "text",
                    "isCategorical": False,
                    "type": "text",
                },
            ],
            "longitudinal": True,
            "groups": [
                {
                    "code": "group",
                    "variables": [
                        {
                            "code": "001",
                            "sql_type": "text",
                            "isCategorical": True,
                            "type": "nominal",
                            "enumerations": ["yes", "no"],
                        }
                    ],
                    "groups": [],
                }
            ],
        }
        expected_message = "Missing 'subjectid' for a longitudinal study at 'DataModel'"
        with self.assertRaisesRegex(InvalidDataModelError, expected_message):
            validate_json(data_model_missing_subjectid)

    def test_data_model_with_deeply_nested_group_errors(self):
        # Test data models with errors in deeply nested groups
        data_model = {
            "code": "DM008",
            "version": "1.0",
            "label": "Deeply Nested Group Errors",
            "variables": [
                {
                    "code": "dataset",
                    "sql_type": "text",
                    "isCategorical": True,
                    "type": "nominal",
                    "enumerations": ["dataset1"],
                }
            ],
            "groups": [
                {
                    "code": "group1",
                    "groups": [{"code": "group2", "variables": [{"code": "deep_var"}]}],
                }  # Invalid variable configuration
            ],
        }
        expected_message = (
            "Missing 'sql_type' in CommonDataElement at '/DM008/group1/group2/deep_var'"
        )
        with self.assertRaisesRegex(InvalidDataModelError, expected_message):
            validate_json(data_model)

    def test_data_model_categorical_variable_without_enumerations(self):
        # Test data models where a categorical variable lacks enumerations
        data_model = {
            "code": "DM009",
            "version": "1.0",
            "label": "Categorical Without Enumerations",
            "variables": [
                {
                    "code": "categorical_var",
                    "sql_type": "text",
                    "isCategorical": True,
                    "type": "nominal",
                }
                # Missing 'enumerations'
            ],
            "groups": [
                {
                    "code": "group",
                    "variables": [
                        {
                            "code": "001",
                            "sql_type": "text",
                            "isCategorical": True,
                            "type": "nominal",
                            "enumerations": ["yes", "no"],
                        }
                    ],
                    "groups": [],
                }
            ],
        }
        expected_message = "Missing 'enumerations' for categorical CommonDataElement at '/DM009/categorical_var'"
        with self.assertRaisesRegex(InvalidDataModelError, expected_message):
            validate_json(data_model)

    def test_duplicate_group_codes(self):
        # Test for duplicate group codes within the data model
        data_model = {
            "code": "DM010",
            "version": "1.0",
            "label": "Data Model with Duplicate Group Codes",
            "variables": [
                {
                    "code": "001",
                    "sql_type": "text",
                    "isCategorical": True,
                    "type": "nominal",
                    "enumerations": ["yes", "no"],
                }
            ],
            "groups": [
                {"code": "group1", "variables": [], "groups": []},
                {
                    "code": "group1",
                    "variables": [],
                    "groups": [],
                },  # Duplicate group code
            ],
        }
        expected_message = "Duplicate Group code 'group1' found at '/DM010'"
        with self.assertRaisesRegex(InvalidDataModelError, expected_message):
            validate_json(data_model)

    def test_data_model_with_deeply_nested_group_errors_updated_path(self):
        # Test data models with errors in deeply nested groups, with updated path
        data_model = {
            "code": "DM008",
            "version": "1.0",
            "label": "Deeply Nested Group Errors",
            "variables": [
                {
                    "code": "dataset",
                    "sql_type": "text",
                    "isCategorical": True,
                    "type": "nominal",
                    "enumerations": ["dataset1"],
                }
            ],
            "groups": [
                {
                    "code": "groupA",
                    "groups": [
                        {
                            "code": "groupB",
                            "variables": [{"code": "deep_var", "sql_type": "int"}],
                        }
                    ],
                }
            ],
        }
        expected_message = "Missing 'isCategorical' in CommonDataElement at '/DM008/groupA/groupB/deep_var'"
        with self.assertRaisesRegex(InvalidDataModelError, expected_message):
            validate_json(data_model)

    def test_variables_not_a_list(self):
        data_model = {
            "code": "DM001",
            "version": "1.0",
            "label": "Test Model",
            "variables": "Not a list",  # Invalid type for variables
            "groups": [],
        }
        with self.assertRaisesRegex(
            InvalidDataModelError,
            "'variables' in DataModel must be a non-empty list of dictionaries",
        ):
            validate_json(data_model)

    def test_variables_empty_list(self):
        data_model = {
            "code": "DM002",
            "version": "1.0",
            "label": "Test Model",
            "variables": [],  # Empty list for variables
            "groups": [{"code": "G001", "variables": [], "groups": []}],
        }
        with self.assertRaisesRegex(
            InvalidDataModelError,
            "'variables' in DataModel must be a non-empty list of dictionaries",
        ):
            validate_json(data_model)

    def test_variables_contains_non_dictionary(self):
        data_model = {
            "code": "DM003",
            "version": "1.0",
            "label": "Test Model",
            "variables": [{}, "Not a dictionary"],  # Contains an invalid entry
            "groups": [{"code": "G001", "variables": [{}], "groups": []}],
        }
        with self.assertRaisesRegex(
            InvalidDataModelError,
            "'variables' in DataModel must contain only dictionaries",
        ):
            validate_json(data_model)

    def test_groups_not_a_list(self):
        data_model = {
            "code": "DM004",
            "version": "1.0",
            "label": "Test Model",
            "variables": [
                {
                    "code": "V001",
                    "sql_type": "text",
                    "isCategorical": True,
                    "type": "nominal",
                }
            ],
            "groups": "Not a list",  # Invalid type for groups
        }
        with self.assertRaisesRegex(
            InvalidDataModelError,
            "'groups' in DataModel must be a non-empty list of dictionaries",
        ):
            validate_json(data_model)

    def test_groups_empty_list(self):
        data_model = {
            "code": "DM005",
            "version": "1.0",
            "label": "Test Model",
            "variables": [
                {
                    "code": "V001",
                    "sql_type": "text",
                    "isCategorical": True,
                    "type": "nominal",
                }
            ],
            "groups": [],  # Empty list for groups
        }
        with self.assertRaisesRegex(
            InvalidDataModelError,
            "'groups' in DataModel must be a non-empty list of dictionaries",
        ):
            validate_json(data_model)

    def test_groups_contains_non_dictionary(self):
        data_model = {
            "code": "DM006",
            "version": "1.0",
            "label": "Test Model",
            "variables": [
                {
                    "code": "V001",
                    "sql_type": "text",
                    "isCategorical": True,
                    "type": "nominal",
                }
            ],
            "groups": [{}, "Not a dictionary"],  # Contains an invalid entry
        }
        with self.assertRaisesRegex(
            InvalidDataModelError,
            "'groups' in DataModel must contain only dictionaries",
        ):
            validate_json(data_model)
