"""Standalone script for converting a CDEs Metadata Schema of the Medical Informatics Platform (MIP) from JSON format back to EXCEL format."""
import pandas as pd

from common_entities import EXCEL_JSON_FIELDS_MAP, EXCEL_COLUMNS, InvalidDataModelError


def extract_values(variable):
    enumerations = variable.get("enumerations")
    if enumerations:
        for elem in enumerations:
            if "code" not in elem or "label" not in elem:
                raise InvalidDataModelError(
                    "Each enumeration must have both 'code' and 'label' fields."
                )

        dict_strings = [
            '{{"{}","{}"}}'.format(
                elem["code"].replace('"', '\\"'), elem["label"].replace('"', '\\"')
            )
            for elem in enumerations
        ]
        return ",".join(dict_strings)

    min_value = variable.get("minValue", "")
    max_value = variable.get("maxValue", "")
    if min_value or max_value:
        return f"{min_value}-{max_value}"
    return ""


def parse_variables(variable, concept_path):
    """Parse individual variables from the json data, handling special cases and constructing the concept path."""
    data_row = []
    for excel_field, json_key in EXCEL_JSON_FIELDS_MAP.items():
        if excel_field == "values":
            value = extract_values(variable)
        elif json_key == "conceptPath":
            concept_path_str = "/".join(concept_path + [variable.get("code", "")])
            value = concept_path_str
        else:
            value = variable.get(json_key, "")
        data_row.append(value)
    return data_row


def recursive_parse_json(json_data, concept_path=[]):
    """Recursively parses JSON data to extract variables and their details.

    Args:
        json_data (dict or list): The JSON data to parse.
        concept_path (list): The path to the current position in the hierarchy.

    Returns:
        list: A list of parsed variables with their details.
    """
    data = []

    if isinstance(json_data, dict):
        # Extract the concept path for the current level
        label = json_data.get("label", json_data.get("code", ""))
        if label:  # Update concept path only if label or code is present
            concept_path.append(label)

        # Process variables at the current level
        for variable in json_data.get("variables") or []:
            data.append(parse_variables(variable, concept_path))

        # Recursively process each group in the current level
        for group in json_data.get("groups") or []:
            data.extend(recursive_parse_json(group, concept_path.copy()))

        if label:  # Ensure concept path is not permanently altered
            concept_path.pop()
    return data


def convert_json_to_excel(cdes_data):

    # Parse the json data to a list of dict items with
    # "csvFile", "name", "code", "type", "values", "unit",
    # "description", "canBeNull", "comments", "conceptPath",
    # and "methodology keys that can be used to create a pandas
    # dataframe
    result = recursive_parse_json(cdes_data)
    # Create a pandas dataframe from the list of dict items
    return pd.DataFrame(result, columns=EXCEL_COLUMNS)
