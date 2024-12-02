import unittest

from converter.excel_to_json import remove_single_variable_group


class TestCleanEmptyFields(unittest.TestCase):
    def test_remove_empty_lists_and_strings(self):
        data = {
            "uuid": "613d49ac-daf0-4ef8-8ae6-e6447cdd5f93",
            "code": "example",
            "version": "1.0",
            "label": "Minimal Example",
            "longitudinal": False,
            "variables": [
                {
                    "code": "dataset",
                    "label": "Dataset Variable",
                    "description": "An example variable description",
                    "sql_type": "text",
                    "isCategorical": True,
                    "enumerations": [{"code": "enum1", "label": "Enumeration 1"}],
                    "type": "nominal",
                    "methodology": "example methodology",
                    "units": "unit",
                }
            ],
            "groups": [
                {
                    "code": "ischemic",
                    "label": "ischemic",
                    "groups": [
                        {
                            "code": "etiology",
                            "label": "etiology",
                            "groups": [
                                {
                                    "code": "rare",
                                    "label": "rare",
                                    "variables": [
                                        {
                                            "label": "Other",
                                            "code": "toast_rareoth",
                                            "type": "nominal",
                                            "description": "TOAST rare: other",
                                            "enumerations": [
                                                {"code": "0", "label": "no"},
                                                {"code": "1", "label": "yes"},
                                                {"code": "9", "label": "unknown"},
                                            ],
                                            "sql_type": "text",
                                            "isCategorical": True,
                                        }
                                    ],
                                }
                            ],
                            "variables": [
                                {
                                    "label": "Dissection",
                                    "code": "toast_cad",
                                    "type": "nominal",
                                    "description": "TOAST: Cervical Artery Dissection",
                                    "enumerations": [
                                        {"code": "0", "label": "no"},
                                        {"code": "1", "label": "yes"},
                                        {"code": "9", "label": "unknown"},
                                    ],
                                    "sql_type": "text",
                                    "isCategorical": True,
                                },
                                {
                                    "label": "LAA",
                                    "code": "toast_laa",
                                    "type": "nominal",
                                    "description": "TOAST, Trial of ORG 10172 in Acute Stroke Treatment classification system: Large Artery Atherosclerosis (>=50% stenosis)",
                                    "enumerations": [
                                        {"code": "0", "label": "no"},
                                        {"code": "1", "label": "yes"},
                                        {"code": "9", "label": "unknown"},
                                    ],
                                    "sql_type": "text",
                                    "isCategorical": True,
                                },
                                {
                                    "label": "Mimic",
                                    "code": "toast_mim",
                                    "type": "nominal",
                                    "description": "TOAST: Stroke or TIA mimic",
                                    "enumerations": [
                                        {"code": "0", "label": "no"},
                                        {"code": "1", "label": "yes"},
                                        {"code": "9", "label": "unknown"},
                                    ],
                                    "sql_type": "text",
                                    "isCategorical": True,
                                },
                                {
                                    "label": "More than one",
                                    "code": "toast_mul",
                                    "type": "nominal",
                                    "description": "TOAST: More than one possible etiology",
                                    "enumerations": [
                                        {"code": "0", "label": "no"},
                                        {"code": "1", "label": "yes"},
                                        {"code": "9", "label": "unknown"},
                                    ],
                                    "sql_type": "text",
                                    "isCategorical": True,
                                },
                                {
                                    "label": "PFO",
                                    "code": "toast_pfo",
                                    "type": "nominal",
                                    "description": "TOAST: Patent Foramen Ovale",
                                    "enumerations": [
                                        {"code": "0", "label": "no"},
                                        {"code": "1", "label": "yes"},
                                        {"code": "9", "label": "unknown"},
                                    ],
                                    "sql_type": "text",
                                    "isCategorical": True,
                                },
                                {
                                    "label": "SVD",
                                    "code": "toast_svd",
                                    "type": "nominal",
                                    "description": "TOAST: Small Vessel Disease",
                                    "enumerations": [
                                        {"code": "0", "label": "no"},
                                        {"code": "1", "label": "yes"},
                                        {"code": "9", "label": "unknown"},
                                    ],
                                    "sql_type": "text",
                                    "isCategorical": True,
                                },
                                {
                                    "label": "Unknown etiology despite complete evaluation",
                                    "code": "toast_unkcmp",
                                    "type": "nominal",
                                    "description": "[0]= No Unknown etiology despite complete evaluation",
                                    "enumerations": [
                                        {"code": "0", "label": "no"},
                                        {"code": "1", "label": "yes"},
                                        {"code": "9", "label": "unknown"},
                                    ],
                                    "sql_type": "text",
                                    "isCategorical": True,
                                },
                                {
                                    "label": "Unknown etiology with incomplete evaluation",
                                    "code": "toast_unkinc",
                                    "type": "nominal",
                                    "description": "[0]= No Unknown etiology with incomplete evaluation",
                                    "enumerations": [
                                        {"code": "0", "label": "no"},
                                        {"code": "1", "label": "yes"},
                                        {"code": "9", "label": "unknown"},
                                    ],
                                    "sql_type": "text",
                                    "isCategorical": True,
                                },
                                {
                                    "label": "CE without PFO",
                                    "code": "toast_ca3",
                                    "type": "nominal",
                                    "description": "TOAST: Cardiac Embolism (excluding PFO or other rare cardiac causes)",
                                    "enumerations": [
                                        {"code": "0", "label": "no"},
                                        {"code": "1", "label": "yes"},
                                        {"code": "9", "label": "unknown"},
                                    ],
                                    "sql_type": "text",
                                    "isCategorical": True,
                                },
                            ],
                        },
                        {
                            "code": "territory",
                            "label": "territory",
                            "groups": [
                                {
                                    "code": "arterial",
                                    "label": "arterial",
                                    "groups": [
                                        {
                                            "code": "MCA",
                                            "label": "MCA",
                                            "variables": [
                                                {
                                                    "label": "Side",
                                                    "code": "isch_local_mca_side",
                                                    "type": "nominal",
                                                    "description": "Ischemic Stroke localisation MCA: side",
                                                    "enumerations": [
                                                        {"code": "1", "label": "right"},
                                                        {"code": "2", "label": "left"},
                                                        {
                                                            "code": "3",
                                                            "label": "bilateral",
                                                        },
                                                        {
                                                            "code": "9",
                                                            "label": "unknown",
                                                        },
                                                    ],
                                                    "sql_type": "text",
                                                    "isCategorical": True,
                                                }
                                            ],
                                        }
                                    ],
                                    "variables": [
                                        {
                                            "label": "ACA",
                                            "code": "isch_local_aca",
                                            "type": "nominal",
                                            "description": "Ischemic Stroke localisation ACA",
                                            "enumerations": [
                                                {"code": "0", "label": "no"},
                                                {"code": "1", "label": "yes"},
                                                {"code": "9", "label": "unknown"},
                                            ],
                                            "sql_type": "text",
                                            "isCategorical": True,
                                        },
                                        {
                                            "label": "MCA",
                                            "code": "isch_local_mca",
                                            "type": "nominal",
                                            "description": "Ischemic Stroke localisation MCA",
                                            "enumerations": [
                                                {"code": "0", "label": "no"},
                                                {"code": "1", "label": "yes"},
                                                {"code": "9", "label": "unknown"},
                                            ],
                                            "sql_type": "text",
                                            "isCategorical": True,
                                        },
                                        {
                                            "label": "PCA",
                                            "code": "isch_local_pca",
                                            "type": "nominal",
                                            "description": "Ischemic Stroke localisation PCA",
                                            "enumerations": [
                                                {"code": "0", "label": "no"},
                                                {"code": "1", "label": "yes"},
                                                {"code": "9", "label": "unknown"},
                                            ],
                                            "sql_type": "text",
                                            "isCategorical": True,
                                        },
                                        {
                                            "label": "Side",
                                            "code": "isch_local_aca_side",
                                            "type": "nominal",
                                            "description": "Ischemic Stroke localisation ACA: side",
                                            "enumerations": [
                                                {"code": "1", "label": "right"},
                                                {"code": "2", "label": "left"},
                                                {"code": "3", "label": "bilateral"},
                                                {"code": "9", "label": "unknown"},
                                            ],
                                            "sql_type": "text",
                                            "isCategorical": True,
                                        },
                                        {
                                            "label": "Side",
                                            "code": "isch_local_pca_side",
                                            "type": "nominal",
                                            "description": "Ischemic Stroke localisation PCA : side",
                                            "enumerations": [
                                                {"code": "1", "label": "right"},
                                                {"code": "2", "label": "left"},
                                                {"code": "3", "label": "bilateral"},
                                                {"code": "9", "label": "unknown"},
                                            ],
                                            "sql_type": "text",
                                            "isCategorical": True,
                                        },
                                    ],
                                }
                            ],
                            "variables": [
                                {
                                    "label": "Infratentorial",
                                    "code": "isch_local_infrat",
                                    "type": "nominal",
                                    "description": "Ischemic Stroke localisation infratentorial",
                                    "enumerations": [
                                        {"code": "0", "label": "no"},
                                        {"code": "1", "label": "yes"},
                                        {"code": "9", "label": "unknown"},
                                    ],
                                    "sql_type": "text",
                                    "isCategorical": True,
                                },
                                {
                                    "label": "Infratentorial side",
                                    "code": "isch_local_infrat_side",
                                    "type": "nominal",
                                    "description": "Ischemic Stroke localisation infratentorial: side",
                                    "enumerations": [
                                        {"code": "1", "label": "right"},
                                        {"code": "2", "label": "left"},
                                        {"code": "3", "label": "bilateral"},
                                        {"code": "9", "label": "unknown"},
                                    ],
                                    "sql_type": "text",
                                    "isCategorical": True,
                                },
                            ],
                        },
                    ],
                }
            ],
        }
        expected = {
            "uuid": "613d49ac-daf0-4ef8-8ae6-e6447cdd5f93",
            "code": "example",
            "version": "1.0",
            "label": "Minimal Example",
            "longitudinal": False,
            "variables": [
                {
                    "code": "dataset",
                    "label": "Dataset Variable",
                    "description": "An example variable description",
                    "sql_type": "text",
                    "isCategorical": True,
                    "enumerations": [{"code": "enum1", "label": "Enumeration 1"}],
                    "type": "nominal",
                    "methodology": "example methodology",
                    "units": "unit",
                }
            ],
            "groups": [
                {
                    "code": "Example Group",
                    "label": "Example Group",
                    "variables": [
                        {
                            "code": "group_variable",
                            "label": "Group Variable",
                            "description": "A variable within a group",
                            "sql_type": "int",
                            "isCategorical": False,
                            "minValue": 0,
                            "maxValue": 100,
                            "type": "integer",
                            "methodology": "group methodology",
                            "units": "years",
                        },
                        {
                            "code": "nested_group_variable",
                            "label": "Nested Group Variable",
                            "description": "A nested group variable",
                            "sql_type": "text",
                            "isCategorical": True,
                            "enumerations": [
                                {
                                    "code": "nested_enum1",
                                    "label": "Nested Enumeration 1",
                                }
                            ],
                            "type": "nominal",
                            "methodology": "nested methodology",
                            "units": "",
                        },
                    ],
                    "groups": [],
                }
            ],
        }
        remove_single_variable_group(data)
        print(data)
        self.assertEqual(data, expected)
        bro = {
            "uuid": "613d49ac-daf0-4ef8-8ae6-e6447cdd5f93",
            "code": "example",
            "version": "1.0",
            "label": "Minimal Example",
            "longitudinal": False,
            "variables": [
                {
                    "code": "dataset",
                    "label": "Dataset Variable",
                    "description": "An example variable description",
                    "sql_type": "text",
                    "isCategorical": True,
                    "enumerations": [{"code": "enum1", "label": "Enumeration 1"}],
                    "type": "nominal",
                    "methodology": "example methodology",
                    "units": "unit",
                }
            ],
            "groups": [
                {
                    "code": "ischemic",
                    "label": "ischemic",
                    "groups": [
                        {
                            "code": "etiology",
                            "label": "etiology",
                            "groups": [],
                            "variables": [
                                {
                                    "label": "Dissection",
                                    "code": "toast_cad",
                                    "type": "nominal",
                                    "description": "TOAST: Cervical Artery Dissection",
                                    "enumerations": [
                                        {"code": "0", "label": "no"},
                                        {"code": "1", "label": "yes"},
                                        {"code": "9", "label": "unknown"},
                                    ],
                                    "sql_type": "text",
                                    "isCategorical": True,
                                },
                                {
                                    "label": "LAA",
                                    "code": "toast_laa",
                                    "type": "nominal",
                                    "description": "TOAST, Trial of ORG 10172 in Acute Stroke Treatment classification system: Large Artery Atherosclerosis (>=50% stenosis)",
                                    "enumerations": [
                                        {"code": "0", "label": "no"},
                                        {"code": "1", "label": "yes"},
                                        {"code": "9", "label": "unknown"},
                                    ],
                                    "sql_type": "text",
                                    "isCategorical": True,
                                },
                                {
                                    "label": "Mimic",
                                    "code": "toast_mim",
                                    "type": "nominal",
                                    "description": "TOAST: Stroke or TIA mimic",
                                    "enumerations": [
                                        {"code": "0", "label": "no"},
                                        {"code": "1", "label": "yes"},
                                        {"code": "9", "label": "unknown"},
                                    ],
                                    "sql_type": "text",
                                    "isCategorical": True,
                                },
                                {
                                    "label": "More than one",
                                    "code": "toast_mul",
                                    "type": "nominal",
                                    "description": "TOAST: More than one possible etiology",
                                    "enumerations": [
                                        {"code": "0", "label": "no"},
                                        {"code": "1", "label": "yes"},
                                        {"code": "9", "label": "unknown"},
                                    ],
                                    "sql_type": "text",
                                    "isCategorical": True,
                                },
                                {
                                    "label": "PFO",
                                    "code": "toast_pfo",
                                    "type": "nominal",
                                    "description": "TOAST: Patent Foramen Ovale",
                                    "enumerations": [
                                        {"code": "0", "label": "no"},
                                        {"code": "1", "label": "yes"},
                                        {"code": "9", "label": "unknown"},
                                    ],
                                    "sql_type": "text",
                                    "isCategorical": True,
                                },
                                {
                                    "label": "SVD",
                                    "code": "toast_svd",
                                    "type": "nominal",
                                    "description": "TOAST: Small Vessel Disease",
                                    "enumerations": [
                                        {"code": "0", "label": "no"},
                                        {"code": "1", "label": "yes"},
                                        {"code": "9", "label": "unknown"},
                                    ],
                                    "sql_type": "text",
                                    "isCategorical": True,
                                },
                                {
                                    "label": "Unknown etiology despite complete evaluation",
                                    "code": "toast_unkcmp",
                                    "type": "nominal",
                                    "description": "[0]= No Unknown etiology despite complete evaluation",
                                    "enumerations": [
                                        {"code": "0", "label": "no"},
                                        {"code": "1", "label": "yes"},
                                        {"code": "9", "label": "unknown"},
                                    ],
                                    "sql_type": "text",
                                    "isCategorical": True,
                                },
                                {
                                    "label": "Unknown etiology with incomplete evaluation",
                                    "code": "toast_unkinc",
                                    "type": "nominal",
                                    "description": "[0]= No Unknown etiology with incomplete evaluation",
                                    "enumerations": [
                                        {"code": "0", "label": "no"},
                                        {"code": "1", "label": "yes"},
                                        {"code": "9", "label": "unknown"},
                                    ],
                                    "sql_type": "text",
                                    "isCategorical": True,
                                },
                                {
                                    "label": "CE without PFO",
                                    "code": "toast_ca3",
                                    "type": "nominal",
                                    "description": "TOAST: Cardiac Embolism (excluding PFO or other rare cardiac causes)",
                                    "enumerations": [
                                        {"code": "0", "label": "no"},
                                        {"code": "1", "label": "yes"},
                                        {"code": "9", "label": "unknown"},
                                    ],
                                    "sql_type": "text",
                                    "isCategorical": True,
                                },
                                {
                                    "label": "Other",
                                    "code": "toast_rareoth",
                                    "type": "nominal",
                                    "description": "TOAST rare: other",
                                    "enumerations": [
                                        {"code": "0", "label": "no"},
                                        {"code": "1", "label": "yes"},
                                        {"code": "9", "label": "unknown"},
                                    ],
                                    "sql_type": "text",
                                    "isCategorical": True,
                                },
                            ],
                        },
                        {
                            "code": "territory",
                            "label": "territory",
                            "groups": [
                                {
                                    "code": "arterial",
                                    "label": "arterial",
                                    "groups": [],
                                    "variables": [
                                        {
                                            "label": "ACA",
                                            "code": "isch_local_aca",
                                            "type": "nominal",
                                            "description": "Ischemic Stroke localisation ACA",
                                            "enumerations": [
                                                {"code": "0", "label": "no"},
                                                {"code": "1", "label": "yes"},
                                                {"code": "9", "label": "unknown"},
                                            ],
                                            "sql_type": "text",
                                            "isCategorical": True,
                                        },
                                        {
                                            "label": "MCA",
                                            "code": "isch_local_mca",
                                            "type": "nominal",
                                            "description": "Ischemic Stroke localisation MCA",
                                            "enumerations": [
                                                {"code": "0", "label": "no"},
                                                {"code": "1", "label": "yes"},
                                                {"code": "9", "label": "unknown"},
                                            ],
                                            "sql_type": "text",
                                            "isCategorical": True,
                                        },
                                        {
                                            "label": "PCA",
                                            "code": "isch_local_pca",
                                            "type": "nominal",
                                            "description": "Ischemic Stroke localisation PCA",
                                            "enumerations": [
                                                {"code": "0", "label": "no"},
                                                {"code": "1", "label": "yes"},
                                                {"code": "9", "label": "unknown"},
                                            ],
                                            "sql_type": "text",
                                            "isCategorical": True,
                                        },
                                        {
                                            "label": "Side",
                                            "code": "isch_local_aca_side",
                                            "type": "nominal",
                                            "description": "Ischemic Stroke localisation ACA: side",
                                            "enumerations": [
                                                {"code": "1", "label": "right"},
                                                {"code": "2", "label": "left"},
                                                {"code": "3", "label": "bilateral"},
                                                {"code": "9", "label": "unknown"},
                                            ],
                                            "sql_type": "text",
                                            "isCategorical": True,
                                        },
                                        {
                                            "label": "Side",
                                            "code": "isch_local_pca_side",
                                            "type": "nominal",
                                            "description": "Ischemic Stroke localisation PCA : side",
                                            "enumerations": [
                                                {"code": "1", "label": "right"},
                                                {"code": "2", "label": "left"},
                                                {"code": "3", "label": "bilateral"},
                                                {"code": "9", "label": "unknown"},
                                            ],
                                            "sql_type": "text",
                                            "isCategorical": True,
                                        },
                                        {
                                            "label": "Side",
                                            "code": "isch_local_mca_side",
                                            "type": "nominal",
                                            "description": "Ischemic Stroke localisation MCA: side",
                                            "enumerations": [
                                                {"code": "1", "label": "right"},
                                                {"code": "2", "label": "left"},
                                                {"code": "3", "label": "bilateral"},
                                                {"code": "9", "label": "unknown"},
                                            ],
                                            "sql_type": "text",
                                            "isCategorical": True,
                                        },
                                    ],
                                }
                            ],
                            "variables": [
                                {
                                    "label": "Infratentorial",
                                    "code": "isch_local_infrat",
                                    "type": "nominal",
                                    "description": "Ischemic Stroke localisation infratentorial",
                                    "enumerations": [
                                        {"code": "0", "label": "no"},
                                        {"code": "1", "label": "yes"},
                                        {"code": "9", "label": "unknown"},
                                    ],
                                    "sql_type": "text",
                                    "isCategorical": True,
                                },
                                {
                                    "label": "Infratentorial side",
                                    "code": "isch_local_infrat_side",
                                    "type": "nominal",
                                    "description": "Ischemic Stroke localisation infratentorial: side",
                                    "enumerations": [
                                        {"code": "1", "label": "right"},
                                        {"code": "2", "label": "left"},
                                        {"code": "3", "label": "bilateral"},
                                        {"code": "9", "label": "unknown"},
                                    ],
                                    "sql_type": "text",
                                    "isCategorical": True,
                                },
                            ],
                        },
                    ],
                }
            ],
        }