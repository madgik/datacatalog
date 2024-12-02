from common_entities import InvalidDataModelError

TYPE_2_SQL = {
    "nominal": ("text", True),
    "real": ("real", False),
    "integer": ("int", False),
    "text": ("text", False),
}


def validate_common_data_element(cde, path):
    required_fields = ["code", "sql_type", "isCategorical", "type"]

    for field in required_fields:
        if field not in cde:
            raise InvalidDataModelError(
                f"Missing '{field}' in CommonDataElement at '{path}'"
            )
    type_key = cde.get("type")
    if type_key not in TYPE_2_SQL:
        raise InvalidDataModelError(
            f"Invalid 'type' in CommonDataElement at '{path}'. Must be one of {list(TYPE_2_SQL.keys())}"
        )

    # Validate sql_type and isCategorical according to the mapping
    expected_sql_type, expected_is_categorical = TYPE_2_SQL[type_key]
    if (
        cde.get("sql_type") != expected_sql_type
        or cde.get("isCategorical") != expected_is_categorical
    ):
        raise InvalidDataModelError(
            f"Mismatch in 'sql_type' or 'isCategorical' for type '{type_key}' in CommonDataElement at '{path}'. "
            f"Expected ('{expected_sql_type}', {expected_is_categorical})"
        )

    if cde.get("isCategorical") and not cde.get("enumerations"):
        raise InvalidDataModelError(
            f"Missing 'enumerations' for categorical CommonDataElement at '{path}'"
        )

    if cde.get("minValue") is not None and cde.get("maxValue") is not None:
        if cde["minValue"] >= cde["maxValue"]:
            raise InvalidDataModelError(
                f"'minValue' >= 'maxValue' in CommonDataElement at '{path}'"
            )


def validate_group(group, path, seen_codes=None, seen_group_codes=None):
    if seen_codes is None:
        seen_codes = set()
    if seen_group_codes is None:
        seen_group_codes = set()

    group_code = group.get("code")
    if not group_code:
        raise InvalidDataModelError(f"Group missing 'code' field at '{path}'")

    # Combine group code with its full path to ensure uniqueness within the hierarchy
    group_path_code = f"{path}/{group_code}"
    if group_path_code in seen_group_codes:
        raise InvalidDataModelError(
            f"Duplicate Group code '{group_code}' found at '{path}'"
        )
    seen_group_codes.add(group_path_code)

    updated_path = f"{path}/{group_code}"

    for variable in group.get("variables") or []:
        code = variable.get("code")
        variable_path_code = f"{updated_path}/{code}"
        if variable_path_code in seen_codes:
            raise InvalidDataModelError(
                f"Duplicate CommonDataElement code '{code}' found in Group '{group_code}' at '{updated_path}'"
            )
        seen_codes.add(variable_path_code)
        validate_common_data_element(variable, variable_path_code)

    for sub_group in group.get("groups") or []:
        validate_group(
            sub_group,
            updated_path,
            seen_codes,
            seen_group_codes,
        )


def validate_json(data_model):
    required_fields = ["code", "version", "label", "variables", "groups"]

    for field in required_fields:
        if field not in data_model:
            raise InvalidDataModelError(f"Missing '{field}' in DataModel")

    # Ensure 'code', 'version', and 'label' are not empty strings
    for field in ["code", "version", "label"]:
        if not isinstance(data_model[field], str) or not data_model[field].strip():
            raise InvalidDataModelError(
                f"'{field}' in DataModel must be a non-empty string"
            )

    # Validate 'variables' and 'groups' are non-empty lists of dictionaries
    if not isinstance(data_model["variables"], list) or not data_model["variables"]:
        raise InvalidDataModelError(
            "'variables' in DataModel must be a non-empty list of dictionaries"
        )
    if not all(isinstance(var, dict) for var in data_model["variables"]):
        raise InvalidDataModelError(
            "'variables' in DataModel must contain only dictionaries"
        )

    if not isinstance(data_model["groups"], list) or not data_model["groups"]:
        raise InvalidDataModelError(
            "'groups' in DataModel must be a non-empty list of dictionaries"
        )
    if not all(isinstance(group, dict) for group in data_model["groups"]):
        raise InvalidDataModelError(
            "'groups' in DataModel must contain only dictionaries"
        )

    # Initialize sets for tracking seen codes and group codes
    seen_codes, seen_group_codes = set(), set()

    validate_group(data_model, "", seen_codes, seen_group_codes)

    if not contains_required_dataset(data_model["variables"], data_model["groups"]):
        raise InvalidDataModelError(
            "The data model must always contain a dataset CommonDataElement"
        )

    if data_model.get("longitudinal"):
        validate_longitudinal_elements(
            data_model["variables"], data_model["groups"], path="DataModel"
        )


def contains_required_dataset(variables, groups, path=""):
    # Check for a 'dataset' CDE in variables
    dataset_present = any(
        v.get("code") == "dataset"
        and v.get("sql_type") == "text"
        and v.get("isCategorical")
        for v in variables
    )
    if dataset_present:
        return True

    # Recursively check in nested groups
    for i, group in enumerate(groups, start=1):
        if contains_required_dataset(
            group.get("variables", []),
            group.get("groups", []),
            path=f"{path}/groups[{i}]",
        ):
            return True

    return False


def validate_longitudinal_elements(variables, groups, path):
    # Check for 'subjectid' and 'visitid' in the top level
    subjectid_present = any(v.get("code") == "subjectid" for v in variables)
    visitid_present = any(v.get("code") == "visitid" for v in variables)

    if not subjectid_present or not visitid_present:
        # If either is missing at the top level, check in nested groups
        for i, group in enumerate(groups, start=1):
            group_path = f"{path}/groups[{i}]"
            subjectid_present = subjectid_present or has_valid_cde_in_group(
                "subjectid", group, group_path
            )
            visitid_present = visitid_present or has_valid_cde_in_group(
                "visitid", group, group_path
            )

    if not subjectid_present:
        raise InvalidDataModelError(
            f"Missing 'subjectid' for a longitudinal study at '{path}'"
        )

    if not visitid_present:
        raise InvalidDataModelError(
            f"Missing 'visitid' that meets the required conditions for a longitudinal study at '{path}'"
        )


def has_valid_cde_in_group(cde_code, group, path):
    """Check for a valid CommonDataElement within a group or nested groups."""
    valid_cde_found = any(v.get("code") == cde_code for v in group.get("variables", []))
    if valid_cde_found:
        return True

    # Recursively check in nested groups
    for i, nested_group in enumerate(group.get("groups", []), start=1):
        if has_valid_cde_in_group(cde_code, nested_group, path=f"{path}/groups[{i}]"):
            return True

    return False
