import unittest

from validator.json_validator import validate_group, InvalidDataModelError


class TestValidateGroup(unittest.TestCase):
    def test_valid_group_with_variables(self):
        # Test a valid group with a list of valid variables
        group = {
            "code": "valid_group_with_variables",
            "variables": [
                {
                    "code": "001",
                    "sql_type": "text",
                    "isCategorical": True,
                    "type": "nominal",
                    "enumerations": ["yes", "no"],
                },
                {
                    "code": "002",
                    "sql_type": "real",
                    "isCategorical": False,
                    "type": "real",
                },
            ],
            "groups": [],
        }
        path = "/test/valid_group_with_variables"
        validate_group(group, path)

    def test_valid_group_with_nested_groups(self):
        # Test a valid group with nested groups containing valid variables
        group = {
            "code": "test",
            "groups": [
                {
                    "code": "valid_group_with_nested_groups",
                    "variables": [
                        {
                            "code": "003",
                            "sql_type": "int",
                            "isCategorical": False,
                            "type": "integer",
                        }
                    ],
                    "groups": [],
                }
            ],
            "variables": [],
        }
        path = "/test/valid_group_with_nested_groups"
        validate_group(group, path)

    def test_group_missing_variables_and_groups(self):
        # Test a group missing both 'variables' and 'groups'
        group = {}
        path = "/test/missing_variables_and_groups"
        with self.assertRaises(InvalidDataModelError):
            validate_group(group, path)

    def test_group_with_invalid_variables(self):
        # Test a group containing invalid variables
        group = {
            "variables": [{"code": "004"}],  # Missing required fields other than 'code'
            "groups": [],
        }
        path = "/test/group_with_invalid_variables"
        with self.assertRaises(InvalidDataModelError):
            validate_group(group, path)

    def test_group_with_invalid_nested_group_structure(self):
        # Test a group with an invalid nested group structure
        group = {
            "groups": [{}],  # Nested group missing both 'variables' and 'groups'
            "variables": [],
        }
        path = "/test/invalid_nested_group_structure"
        with self.assertRaises(InvalidDataModelError):
            validate_group(group, path)

    def test_group_with_deeply_nested_groups(self):
        # Test a group with deeply nested groups containing valid variables
        group = {
            "code": "test",
            "groups": [
                {
                    "code": "deeply_nested_group",
                    "groups": [
                        {
                            "code": "deeply_deeply_nested_group",
                            "variables": [
                                {
                                    "code": "101",
                                    "sql_type": "text",
                                    "isCategorical": True,
                                    "type": "nominal",
                                    "enumerations": ["A", "B", "C"],
                                }
                            ],
                            "groups": [],
                        }
                    ],
                    "variables": [],
                }
            ],
            "variables": [],
        }
        path = ""
        validate_group(group, path)

    def test_group_with_mixed_valid_and_invalid_variables(self):
        # Test a group containing both valid and invalid variables
        group = {
            "variables": [
                {
                    "code": "102",
                    "sql_type": "int",
                    "isCategorical": False,
                    "type": "integer",
                },  # Valid
                {"code": "103"},  # Invalid, missing required fields other than 'code'
            ],
            "groups": [],
        }
        path = "/test/mixed_valid_and_invalid_variables"
        with self.assertRaises(InvalidDataModelError):
            validate_group(group, path)

    def test_valid_group_with_empty_variables_and_non_empty_groups(self):
        # Test a valid group scenario with empty variables but non-empty nested groups
        group = {
            "code": "test",
            "groups": [
                {
                    "code": "valid_group_empty_variables",
                    "variables": [
                        {
                            "code": "104",
                            "sql_type": "real",
                            "isCategorical": False,
                            "type": "real",
                        }
                    ],
                    "groups": [],
                }
            ],
            "variables": [],  # Intentionally empty
        }
        path = "/test/valid_group_empty_variables"
        validate_group(group, path)

    def test_group_with_all_invalid_variables(self):
        # Test a group where all variables are invalid
        group = {
            "variables": [
                {
                    "sql_type": "text"
                },  # Invalid, missing 'code', 'isCategorical', and 'type'
                {},  # Completely invalid
            ],
            "groups": [],
        }
        path = "/test/all_invalid_variables"
        with self.assertRaises(InvalidDataModelError):
            validate_group(group, path)

    def test_group_with_valid_and_invalid_nested_groups(self):
        # Test a group containing a mix of valid and invalid nested groups
        group = {
            "groups": [
                {
                    "variables": [
                        {
                            "code": "105",
                            "sql_type": "text",
                            "isCategorical": True,
                            "type": "nominal",
                            "enumerations": ["X", "Y"],
                        }
                    ],
                    "groups": [],
                },
                {},  # Invalid nested group
            ],
            "variables": [],
        }
        path = "/test/mixed_valid_invalid_nested_groups"
        with self.assertRaises(InvalidDataModelError):
            validate_group(group, path)

    def test_duplicate_codes_within_same_group(self):
        # Test case where duplicate CDE codes exist within the same group
        group = {
            "variables": [
                {
                    "code": "001",
                    "sql_type": "text",
                    "isCategorical": True,
                    "type": "nominal",
                    "enumerations": ["X", "Y"],
                },
                {
                    "code": "001",
                    "sql_type": "int",
                    "isCategorical": False,
                    "type": "integer",
                },
            ],
            "groups": [],
        }
        path = "/test/duplicate_within_group"
        with self.assertRaises(InvalidDataModelError):
            validate_group(group, path)

    def test_duplicate_codes_across_nested_groups(self):
        # Test case where a CDE code is duplicated across nested groups
        group = {
            "variables": [],
            "groups": [
                {
                    "variables": [
                        {
                            "code": "002",
                            "sql_type": "text",
                            "isCategorical": True,
                            "type": "nominal",
                            "enumerations": ["X", "Y"],
                        }
                    ],
                    "groups": [],
                },
                {
                    "variables": [
                        {
                            "code": "002",
                            "sql_type": "real",
                            "isCategorical": False,
                            "type": "real",
                        }
                    ],
                    "groups": [],
                },
            ],
        }
        path = "/test/duplicate_across_groups"
        with self.assertRaises(InvalidDataModelError):
            validate_group(group, path, seen_codes=set())
