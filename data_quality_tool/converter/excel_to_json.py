import pandas as pd
import json

from common_entities import (
    EXCEL_TYPE_2_SQL_TYPE_ISCATEGORICAL_MAP,
    InvalidDataModelError,
)


EXCEL_JSON_FIELDS_MAP_WITHOUT_VALUES = {
    "name": "label",
    "code": "code",
    "type": "type",
    "unit": "units",
    "description": "description",
    "canBeNull": "canBeNull",
    "comments": "comments",
    "conceptPath": "conceptPath",
    "methodology": "methodology",
}


def process_enumerations(values):
    """
    Parses a custom-formatted string into a list of dictionaries with 'code' and 'label'.
    Expected format: '{"code1", "label1"}, {"code2", "label2"}'.
    """
    # Transform the string to a JSON-compatible format
    try:
        # Transforming {"key","value"} into [{"key": "value"}]
        transformed_values = (
            "[" + values.replace('","', '":"').replace('", "', '": "') + "]"
        )
        enumerations = json.loads(transformed_values)
    except json.JSONDecodeError:
        raise InvalidDataModelError(
            'Nominal values format error: \'{"code", "label"}, {"code", "label"}\' expected but got '
            + values
            + "."
        )
    return [
        {"code": list(item.keys())[0], "label": list(item.values())[0]}
        for item in enumerations
    ]


def insert_variable_into_structure(root, variable, path):
    """
    Insert a variable into the hierarchical structure based on the provided path.
    """
    # The last path element of the list is always the variable.
    for part in path[:-1]:
        # Find or create the group at the current level
        found = False
        for group in root["groups"]:
            if group["code"] == part:
                root = group
                found = True
                break

        if not found:
            new_group = {"code": part, "label": part, "groups": [], "variables": []}
            root["groups"].append(new_group)
            root = new_group

    root["variables"].append(variable)


def process_values_based_on_type(row, variable):
    """
    Processes the 'values' field based on the variable's 'type':
    - For 'integer' or 'real', extracts 'minValue' and 'maxValue' from a range specified in 'values'
      and ensures these values are of the appropriate type.
    - For 'nominal', retrieves a list of 'enumerations' from 'values'.
    """
    code = row.get("code")
    values = row.get("values")
    variable_type = row.get("type")

    if variable_type in ["real", "integer"] and values:
        try:
            # Attempt to split the string into exactly two parts and unpack
            min_value, max_value = values.split("-")

            # Try to convert both parts into floats
            float(min_value)
            float(max_value)
        except Exception:
            raise InvalidDataModelError(
                f"Values must match format '<float or integer>-<float or integer>' but got '{values}'."
            )

        # Convert min and max values to the appropriate type
        try:
            if variable_type == "integer":
                variable["minValue"], variable["maxValue"] = int(min_value), int(
                    max_value
                )
            elif variable_type == "real":
                variable["minValue"], variable["maxValue"] = float(min_value), float(
                    max_value
                )
        except ValueError:
            raise InvalidDataModelError(
                f"Range values for variable {code} must be valid {variable_type} numbers"
            )

    elif variable_type == "nominal":
        if not values:
            raise InvalidDataModelError(
                f"The 'values' should not be empty for variable {code} when type is 'nominal'"
            )
        variable["enumerations"] = process_enumerations(values)


def validate_variable_type(row):
    valid_types = set(EXCEL_TYPE_2_SQL_TYPE_ISCATEGORICAL_MAP.keys())
    if "type" not in row or row["type"] not in valid_types:
        valid_types_str = ", ".join(valid_types)
        raise InvalidDataModelError(
            f"The row must have a 'type' field with a valid value."
            f" Valid values are: {valid_types_str}, got '{row.get('type')}' instead."
        )


def process_variable(row):
    """
    Processes a single row into a variable dictionary, applying validations
    and transformations based on the row's data.
    """
    # Validate variable type first
    validate_variable_type(row)

    # Initialize the variable dictionary with mappings from EXCEL_JSON_FIELDS_MAP_WITHOUT_VALUES
    variable = {
        json_key: row[excel_col]
        for excel_col, json_key in EXCEL_JSON_FIELDS_MAP_WITHOUT_VALUES.items()
        if excel_col in row and pd.notnull(row[excel_col])
    }

    # Process 'values' based on variable type, which might modify 'variable' in-place
    process_values_based_on_type(row, variable)

    (
        variable["sql_type"],
        variable["isCategorical"],
    ) = EXCEL_TYPE_2_SQL_TYPE_ISCATEGORICAL_MAP[variable["type"]]

    return variable


def remove_single_variable_group(group, parent=None):
    if "groups" in group:
        # Process subgroups recursively
        for subgroup in group["groups"]:
            remove_single_variable_group(subgroup, group)

        # After processing subgroups, check if any subgroup meets the criteria
        groups_to_remove = []
        for subgroup in group["groups"]:
            if "groups" not in subgroup:
                if "variables" not in group:
                    group["variables"] = []
                if len(subgroup.get("variables", [])) == 1:
                    group["variables"].append(subgroup["variables"][0])
                    groups_to_remove.append(subgroup)

        # Remove the subgroups that have been processed
        for subgroup in groups_to_remove:
            group["groups"].remove(subgroup)

        # If current group has only one variable after processing, move it up to the parent group
        if (
            "variables" in group
            and parent is not None
            and len(group["variables"]) == 1
            and not group["groups"]
        ):
            if "variables" not in parent:
                parent["variables"] = []
            parent["variables"].append(group["variables"][0])
            parent["groups"].remove(group)


def clean_empty_fields(data):
    if isinstance(data, dict):  # If the item is a dictionary
        keys_to_delete = [
            key
            for key, value in data.items()
            if (key in ["variables", "groups", "enumerations"] and not value)
            or value == ""
        ]
        for key in keys_to_delete:
            del data[
                key
            ]  # Delete the key if its value is an empty list or an empty string
        for key in data:  # Recursively clean remaining dictionary items
            clean_empty_fields(data[key])
    elif isinstance(data, list):
        # If the item is a list, apply the function to each element
        for item in data:
            clean_empty_fields(item)


def convert_excel_to_json(df):
    """
    Converts a DataFrame from Excel into a JSON structure, handling enumerations specifically,
    and adds 'isCategorical' and 'sql_type' based on the 'type'.
    """
    df = df.astype(str).replace("nan", None)
    root = {"variables": [], "groups": [], "code": "root"}

    for _, row in df.iterrows():
        try:

            variable = process_variable(row.to_dict())
            if "conceptPath" in variable and variable["conceptPath"] and variable["conceptPath"] != "None":
                path = variable["conceptPath"].split("/")
                del variable["conceptPath"]
                insert_variable_into_structure(root, variable, path)
            else:
                raise InvalidDataModelError(
                    f"The variable {variable['code']} is missing the conceptPath"
                )
        except InvalidDataModelError as e:
            raise InvalidDataModelError(f"Error processing variable: {e}")

    if root["groups"]:
        data_model = root["groups"][0]
        data_model["version"] = "to be defined"
        groups_to_process = list(data_model["groups"])
        for group in groups_to_process:
            remove_single_variable_group(group, data_model)
        clean_empty_fields(data_model)

        return data_model
    else:
        return {"code": "No groups found", "groups": [], "variables": root["variables"]}
