import unittest

from validator.json_validator import (
    validate_longitudinal_elements,
    InvalidDataModelError,
)


class TestValidateLongitudinalElements(unittest.TestCase):
    def test_longitudinal_elements_at_top_level(self):
        # Both elements present at the top level
        variables = [
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
        ]
        groups = []
        path = "DataModel"
        validate_longitudinal_elements(variables, groups, path)

    def test_longitudinal_elements_within_nested_group(self):
        # Elements within a nested group
        variables = []
        groups = [
            {
                "variables": [
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
                "groups": [],
            }
        ]
        path = "DataModel/Group"
        validate_longitudinal_elements(variables, groups, path)

    def test_absence_of_longitudinal_elements(self):
        # Missing both 'subjectid' and 'visitid'
        variables = []
        groups = []
        path = "DataModel"
        with self.assertRaises(InvalidDataModelError):
            validate_longitudinal_elements(variables, groups, path)

    def test_longitudinal_elements_spread_across_levels(self):
        # 'subjectid' at the top level, 'visitid' within a nested group
        variables = [
            {
                "code": "subjectid",
                "sql_type": "text",
                "isCategorical": False,
                "type": "text",
            }
        ]
        groups = [
            {
                "variables": [
                    {
                        "code": "visitid",
                        "sql_type": "text",
                        "isCategorical": False,
                        "type": "text",
                    }
                ],
                "groups": [],
            }
        ]
        path = "DataModel"
        validate_longitudinal_elements(variables, groups, path)

    def test_multiple_instances_of_longitudinal_elements(self):
        # Multiple 'subjectid' and 'visitid' across the data model
        variables = [
            {
                "code": "subjectid",
                "sql_type": "text",
                "isCategorical": False,
                "type": "text",
            }
        ]
        groups = [
            {
                "variables": [
                    {
                        "code": "visitid",
                        "sql_type": "text",
                        "isCategorical": False,
                        "type": "text",
                    },
                    {
                        "code": "subjectid",
                        "sql_type": "text",
                        "isCategorical": False,
                        "type": "text",
                    },  # Another instance
                ],
                "groups": [],
            }
        ]
        path = "DataModel"
        validate_longitudinal_elements(variables, groups, path)

    def test_longitudinal_elements_missing_visit_id(self):
        variables = [
            {
                "code": "subjectid",
                "sql_type": "text",
                "isCategorical": False,
                "type": "text",
            }
        ]
        groups = []
        path = "DataModel"
        with self.assertRaises(InvalidDataModelError):
            validate_longitudinal_elements(variables, groups, path)

    def test_deeply_nested_longitudinal_elements(self):
        # 'visitid' deeply nested within groups
        variables = [
            {
                "code": "subjectid",
                "sql_type": "text",
                "isCategorical": False,
                "type": "text",
            }
        ]
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
                                        "code": "visitid",
                                        "sql_type": "text",
                                        "isCategorical": False,
                                        "type": "text",
                                    }
                                ],
                                "groups": [],
                            }
                        ],
                    }
                ],
            }
        ]
        path = "DataModel"
        validate_longitudinal_elements(variables, groups, path)
