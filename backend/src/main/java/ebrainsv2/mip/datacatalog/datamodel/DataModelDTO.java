package ebrainsv2.mip.datacatalog.datamodel;

import java.util.List;
import java.util.UUID;

import static ebrainsv2.mip.datacatalog.datamodel.DataModelValidator.containsRequiredDataset;
import static ebrainsv2.mip.datacatalog.datamodel.DataModelValidator.validateLongitudinalElements;

public record DataModelDTO(
        UUID uuid,
        String code,
        String version,
        String label,
        Boolean longitudinal,
        List<CommonDataElementDTO> variables,
        List<DataModelMetadataGroupDTO> groups,
        Boolean released
) {
    public DataModelDTO {
        validateField(code, "code");
        validateField(version, "version");
        validateField(label, "label");
        validateField(variables, "variables");
        validateField(groups, "groups");

        if (!containsRequiredDataset(variables, groups)) {
            throw new InvalidDataModelError("The data model must always contain a dataset CommonDataElement.");
        }

        if (Boolean.TRUE.equals(longitudinal)) {
            validateLongitudinalElements(variables, groups);
        }
    }

    private void validateField(Object field, String fieldName) {
        if (field == null || (field instanceof String && ((String) field).isEmpty())) {
            throw new InvalidDataModelError(String.format("Data model's field '%s' is required and must not be null or empty.", fieldName));
        } else if (field instanceof List && ((List<?>) field).isEmpty()) {
            throw new InvalidDataModelError(String.format("Data model's field '%s' is required and must not be an empty list.", fieldName));
        }
    }
}

