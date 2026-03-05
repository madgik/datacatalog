import pandas as pd
import json
import re
from urllib.parse import unquote

from common_entities import (
    EXCEL_TYPE_2_SQL_TYPE_ISCATEGORICAL_MAP,
    InvalidDataModelError,
)
from converter.json_to_excel import ROOT_METADATA_CODE, ROOT_METADATA_PREFIX


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

    if not isinstance(enumerations, list) or any(
        not isinstance(item, dict) for item in enumerations
    ):
        raise InvalidDataModelError(
            'Nominal values format error: \'{"code", "label"}, {"code", "label"}\' expected but got '
            + str(values)
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
        group_code = part

        # Find or create the group at the current level
        found = False
        for group in root["groups"]:
            if group["code"] == group_code:
                root = group
                found = True
                break

        if not found:
            new_group = {
                "code": group_code,
                "label": group_code,
                "groups": [],
                "variables": [],
            }
            root["groups"].append(new_group)
            root = new_group

    root["variables"].append(variable)


def process_values_based_on_type(row, variable):
    """
    Processes the 'values' field based on the variable's 'type':
    - For 'integer' or 'real', extracts 'minValue' and 'maxValue' from a range specified in 'values'
      and ensures these values are of the appropriate type.
      If 'type' is 'integer' but the parsed bounds aren't whole numbers, raises DatasetError.
    - For 'nominal', retrieves a list of 'enumerations' from 'values'.
    """
    code = row.get("code")
    values = row.get("values")
    variable_type = row.get("type")

    if variable_type in ["real", "integer"] and values:
        values = str(values)
        # Split on the last hyphen only
        parts = values.rsplit("-", 1)
        if len(parts) != 2:
            raise InvalidDataModelError(
                f"Values must match format '<float or integer>-<float or integer>' but got '{values}'."
            )

        min_str, max_str = parts[0].strip(), parts[1].strip()

        # Parse both ends as floats first
        try:
            min_val = float(min_str)
            max_val = float(max_str)
        except ValueError:
            raise InvalidDataModelError(
                f"Range values for variable {code} must be valid numbers but got '{values}'."
            )

        if variable_type == "integer":
            # If either bound has a fractional part, that's invalid for integer variables
            if not min_val.is_integer() or not max_val.is_integer():
                raise InvalidDataModelError(
                    f"Variable {code} declared as integer but range bounds '{values}' are not whole numbers."
                )
            # Safe to cast to int
            variable["minValue"] = int(min_val)
            variable["maxValue"] = int(max_val)
        else:  # real
            variable["minValue"] = _parse_number_preserving_integer(min_str)
            variable["maxValue"] = _parse_number_preserving_integer(max_str)

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
    # This is used only in the case that we want to extract from a tree only the variables that actually have values,
    # so that the tree has a more clear structure.
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
    df = df.where(pd.notna(df), None)
    metadata, df = _extract_root_metadata(df)
    roundtrip_hints = metadata.pop("__dqt_roundtrip_hints", None)

    root = {"variables": [], "groups": [], "code": "root"}

    for _, row in df.iterrows():
        try:

            variable = process_variable(row.to_dict())
            if (
                "conceptPath" in variable
                and variable["conceptPath"]
                and variable["conceptPath"] != "None"
            ):
                path = [
                    part.strip() for part in str(variable["conceptPath"]).split("/")
                ]
                del variable["conceptPath"]
                insert_variable_into_structure(root, variable, path)
            else:
                raise InvalidDataModelError(
                    f"The variable {variable['code']} is missing the conceptPath"
                )
        except InvalidDataModelError as e:
            raise InvalidDataModelError(f"Error processing variable: {e}")

    if not root["groups"] and not root["variables"]:
        if metadata:
            data_model = {
                "code": metadata.get("code", "No groups found"),
                "label": metadata.get("label", metadata.get("code", "No groups found")),
                "version": metadata.get("version", "to be defined"),
                "groups": [],
                "variables": [],
            }
        else:
            return {"code": "No groups found", "groups": [], "variables": []}
    else:
        root_group_key = metadata.get("label", metadata.get("code"))
        top_level_group = None
        if root_group_key:
            top_level_group = next(
                (
                    group
                    for group in root["groups"]
                    if group.get("code") == root_group_key
                ),
                None,
            )

        if top_level_group is None and len(root["groups"]) == 1:
            top_level_group = root["groups"][0]

        if top_level_group is not None:
            top_groups = [
                group for group in root["groups"] if group is not top_level_group
            ]
            data_model = {
                "code": metadata.get("code", top_level_group["code"]),
                "label": metadata.get(
                    "label", top_level_group.get("label", top_level_group["code"])
                ),
                "version": metadata.get("version", "to be defined"),
                "variables": top_level_group.get("variables", []),
                "groups": top_level_group.get("groups", []) + top_groups,
            }
        else:
            data_model = {
                "code": metadata.get("code", "DataModel"),
                "label": metadata.get("label", metadata.get("code", "DataModel")),
                "version": metadata.get("version", "to be defined"),
                "variables": root["variables"],
                "groups": root["groups"],
            }

    for key, value in metadata.items():
        if key not in {"code", "label", "version"}:
            data_model[key] = value

    clean_empty_fields(data_model)
    data_model.setdefault("groups", [])
    _apply_roundtrip_hints(data_model, roundtrip_hints)
    return data_model


def _parse_number_preserving_integer(value):
    if isinstance(value, (int, float)):
        return value

    value = str(value).strip()
    if re.fullmatch(r"[+-]?\d+", value):
        return int(value)
    return float(value)


def _extract_root_metadata(df):
    if "code" not in df.columns or "csvFile" not in df.columns:
        return {}, df

    metadata_mask = df["code"].apply(
        lambda value: str(value) == ROOT_METADATA_CODE
    ) & df["csvFile"].apply(
        lambda value: isinstance(value, str) and value.startswith(ROOT_METADATA_PREFIX)
    )
    if not metadata_mask.any():
        return {}, df

    metadata_rows = df[metadata_mask]
    if len(metadata_rows) > 1:
        raise InvalidDataModelError("Multiple root metadata rows found in Excel input.")

    metadata_row = metadata_rows.iloc[0]
    encoded_metadata = metadata_row.get("csvFile")
    payload = encoded_metadata[len(ROOT_METADATA_PREFIX) :]
    try:
        metadata = json.loads(unquote(payload))
    except json.JSONDecodeError:
        raise InvalidDataModelError("Invalid root metadata row in Excel input.")
    if not isinstance(metadata, dict):
        raise InvalidDataModelError("Invalid root metadata row in Excel input.")

    filtered_df = df[~metadata_mask].copy()
    return metadata, filtered_df


def _apply_roundtrip_hints(data_model, hints):
    if not isinstance(hints, dict):
        return

    variable_fields = [
        field
        for field in hints.get("variable_fields_with_explicit_empty", [])
        if field not in {"enumerations", "minValue", "maxValue"}
    ]
    enumeration_fields = hints.get("enumeration_fields_with_explicit_empty", [])

    def _walk(node):
        for variable in node.get("variables") or []:
            for field in variable_fields:
                if field not in variable:
                    variable[field] = ""

            for enumeration in variable.get("enumerations") or []:
                if isinstance(enumeration, dict):
                    for field in enumeration_fields:
                        if field not in enumeration:
                            enumeration[field] = ""

        for group in node.get("groups") or []:
            _walk(group)

    _walk(data_model)
