import unittest

from validator.json_validator import contains_required_dataset


class TestContainsRequiredDataset(unittest.TestCase):
    def test_dataset_present_in_variables(self):
        # Dataset CDE is directly in the variables list
        variables = [{"code": "dataset", "sql_type": "text", "isCategorical": True}]
        groups = []
        self.assertTrue(contains_required_dataset(variables, groups))

    def test_dataset_present_in_nested_group(self):
        # Dataset CDE is within a nested group
        variables = []
        groups = [
            {
                "variables": [
                    {"code": "dataset", "sql_type": "text", "isCategorical": True}
                ],
                "groups": [],
            }
        ]
        self.assertTrue(contains_required_dataset(variables, groups))

    def test_dataset_absent(self):
        # Dataset CDE is absent
        variables = [{"code": "other_var", "sql_type": "real", "isCategorical": False}]
        groups = []
        self.assertFalse(contains_required_dataset(variables, groups))

    def test_dataset_deeply_nested(self):
        # Dataset CDE is deeply nested within groups
        variables = []
        groups = [
            {
                "variables": [],
                "groups": [
                    {
                        "variables": [],
                        "groups": [
                            {
                                "variables": [
                                    {
                                        "code": "dataset",
                                        "sql_type": "text",
                                        "isCategorical": True,
                                    }
                                ],
                                "groups": [],
                            }
                        ],
                    }
                ],
            }
        ]
        self.assertTrue(contains_required_dataset(variables, groups))

    def test_deeply_nested_without_dataset(self):
        # Multiple nested levels without the dataset CDE
        variables = []
        groups = [
            {
                "variables": [],
                "groups": [
                    {
                        "variables": [],
                        "groups": [
                            {
                                "variables": [],
                                "groups": [],
                            }  # Deeply nested but no dataset
                        ],
                    }
                ],
            }
        ]
        self.assertFalse(contains_required_dataset(variables, groups))

    def test_multiple_datasets_in_different_locations(self):
        # Multiple dataset CDEs in different locations
        variables = [{"code": "dataset", "sql_type": "text", "isCategorical": True}]
        groups = [
            {
                "variables": [
                    {"code": "dataset", "sql_type": "text", "isCategorical": True}
                ],
                "groups": [],
            }
        ]
        self.assertTrue(contains_required_dataset(variables, groups))

    def test_edge_cases_empty_lists(self):
        # Both variables and groups are empty lists
        variables = []
        groups = []
        self.assertFalse(contains_required_dataset(variables, groups))

    def test_misspelled_dataset_code(self):
        # Dataset code is misspelled
        variables = [{"code": "datast", "sql_type": "text", "isCategorical": True}]
        groups = []
        self.assertFalse(contains_required_dataset(variables, groups))
