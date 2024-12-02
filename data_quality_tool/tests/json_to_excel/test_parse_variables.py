import unittest

from converter.json_to_excel import parse_variables


class TestParseVariablesFunction(unittest.TestCase):
    def setUp(self):
        self.basic_variable = {
            "code": "V1",
            "label": "Variable 1",
            "type": "integer",
            "enumerations": [{"code": "1", "label": "One"}],
            "units": "units",
            "description": "A basic variable.",
        }

    def test_complete_variable(self):
        concept_path = ["Group"]
        expected = [
            "",  # csvFile is not present in the basic_variable
            "Variable 1",
            "V1",
            "integer",
            '{"1","One"}',
            "units",
            "A basic variable.",
            "",  # canBeNull is not present in the basic_variable
            "",  # comments is not present in the basic_variable
            "Group/V1",
            "",  # methodology is not present in the basic_variable
        ]
        self.assertEqual(parse_variables(self.basic_variable, concept_path), expected)

    def test_variable_missing_fields(self):
        variable_missing_fields = {"code": "V2", "label": "Variable 2"}
        concept_path = ["Group"]
        expected = [
            "",  # csvFile is not present
            "Variable 2",
            "V2",
            "",  # type is missing
            "",  # values is handled by extract_values, expected to be empty
            "",  # units is missing
            "",  # description is missing
            "",  # canBeNull is not present
            "",  # comments is not present
            "Group/V2",
            "",  # methodology is missing
        ]
        self.assertEqual(
            parse_variables(variable_missing_fields, concept_path), expected
        )

    def test_with_complex_concept_path(self):
        variable = {"code": "V3", "label": "Variable 3", "type": "string"}
        concept_path = ["Group", "Subgroup", "Sub-subgroup"]
        expected_concept_path = "Group/Subgroup/Sub-subgroup/V3"
        result = parse_variables(variable, concept_path)
        self.assertIn(expected_concept_path, result)

    def test_handling_special_characters_in_concept_path(self):
        variable = {"code": "V4", "label": "Variable 4", "type": "date"}
        concept_path = ["Group with space", "Subgroup&Special", "Sub-subgroup/Special"]
        expected_concept_path = (
            "Group with space/Subgroup&Special/Sub-subgroup/Special/V4"
        )
        result = parse_variables(variable, concept_path)
        self.assertIn(expected_concept_path, result)
