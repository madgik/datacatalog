package ebrainsv2.mip.datacatalog.datamodel;


import java.util.List;
import java.util.Set;

public record CommonDataElementDTO(
        String code,
        String label,
        String description,
        String sql_type,
        Boolean isCategorical,
        List<EnumerationDTO> enumerations,
        Integer minValue,
        Integer maxValue,
        String type,
        String methodology,
        String units
) {
    public CommonDataElementDTO {
        validateField(code, "code", code);
        validateField(label, "label", code);
        validateField(sql_type, "sql_type", code);
        validateField(type, "type", code);


        if (Boolean.TRUE.equals(isCategorical) && (enumerations == null || enumerations.isEmpty())) {
            throw new InvalidDataModelError("The CDE " + code + " has 'is_categorical' set to True but there are no enumerations.");
        }

        // Check minValue and maxValue values
        if (minValue != null && maxValue != null && minValue >= maxValue) {
            throw new InvalidDataModelError("The CDE " + code + " has minValue greater than or equal to maxValue.");
        }

        // Validate 'type' field against valid types
        Set<String> validTypes = Set.of("nominal", "real", "integer", "text");
        if (!validTypes.contains(type)) {
            throw new InvalidDataModelError("The CDE " + code + " has an invalid 'type'. Valid types are: " + validTypes);
        }
    }
    
    private static void validateField(Object field, String fieldName, String code) {
        if (field == null || (field instanceof String && ((String) field).isEmpty())) {
            throw new InvalidDataModelError(String.format("Element: '%s' is missing from the CDE %s", fieldName, code));
        }
    }
    
    public record EnumerationDTO(String code, String label) {
    }

}

