import unittest

from converter.excel_to_json import insert_variable_into_structure


class TestInsertVariableIntoStructure(unittest.TestCase):
    def setUp(self):
        self.root = {"groups": [], "variables": []}

    def test_insert_single_variable(self):
        variable = {"code": "V1", "label": "Variable 1"}
        path = ["Group1", "V1"]
        insert_variable_into_structure(self.root, variable, path)
        self.assertEqual(len(self.root["groups"]), 1)
        self.assertEqual(len(self.root["groups"][0]["variables"]), 1)
        self.assertEqual(self.root["groups"][0]["variables"][0], variable)

    def test_insert_variables_at_different_levels(self):
        variable1 = {"code": "V1", "label": "Variable 1"}
        path1 = ["Group1", "V1"]
        variable2 = {"code": "V2", "label": "Variable 2"}
        path2 = ["Group1", "Subgroup1", "V2"]
        insert_variable_into_structure(self.root, variable1, path1)
        insert_variable_into_structure(self.root, variable2, path2)
        self.assertEqual(len(self.root["groups"]), 1)
        self.assertEqual(len(self.root["groups"][0]["groups"]), 1)
        self.assertEqual(len(self.root["groups"][0]["groups"][0]["variables"]), 1)
        self.assertEqual(self.root["groups"][0]["groups"][0]["variables"][0], variable2)

    def test_insert_variable_same_group(self):
        variable1 = {"code": "V1", "label": "Variable 1"}
        variable2 = {"code": "V2", "label": "Variable 2"}
        path = ["Group1", "V1"]
        insert_variable_into_structure(self.root, variable1, path)
        path = ["Group1", "V2"]
        insert_variable_into_structure(self.root, variable2, path)
        self.assertEqual(len(self.root["groups"]), 1)
        self.assertEqual(len(self.root["groups"][0]["variables"]), 2)

    def test_deeply_nested_structure(self):
        variable = {"code": "VDeep", "label": "Deep Variable"}
        path = ["Group1", "Subgroup1", "SubSubgroup1", "SubSubSubgroup1", "VDeep"]
        insert_variable_into_structure(self.root, variable, path)
        # Verify that the structure is correctly nested
        self.assertEqual(
            len(self.root["groups"][0]["groups"][0]["groups"][0]["groups"]), 1
        )
        self.assertEqual(
            self.root["groups"][0]["groups"][0]["groups"][0]["groups"][0]["variables"][
                0
            ],
            variable,
        )

    def test_duplicate_variable_in_different_groups(self):
        variable1 = {"code": "VDup", "label": "Duplicate Variable"}
        path1 = ["Group1", "VDup"]
        variable2 = {"code": "VDup", "label": "Duplicate Variable"}
        path2 = ["Group2", "VDup"]
        insert_variable_into_structure(self.root, variable1, path1)
        insert_variable_into_structure(self.root, variable2, path2)
        # Verify that both variables are correctly inserted into separate groups
        self.assertEqual(len(self.root["groups"]), 2)
        self.assertEqual(
            self.root["groups"][0]["variables"][0],
            self.root["groups"][1]["variables"][0],
        )

    def test_special_characters_in_group_code(self):
        variable = {"code": "VSpecial", "label": "Special Variable"}
        path = ["Group$1&", "Subgroup*2@", "VSpecial"]
        insert_variable_into_structure(self.root, variable, path)
        # Verify the group with special characters is created and contains the variable
        self.assertTrue(
            any(group["code"] == "Group$1&" for group in self.root["groups"])
        )
        subgroup = self.root["groups"][0]["groups"][0]
        self.assertEqual(subgroup["code"], "Subgroup*2@")
        self.assertEqual(subgroup["variables"][0], variable)

    def test_inserting_variable_without_group(self):
        variable = {"code": "VNoGroup", "label": "No Group Variable"}
        path = ["VNoGroup"]
        insert_variable_into_structure(self.root, variable, path)
        # Verify variable is inserted at the root level
        self.assertIn(variable, self.root["variables"])
