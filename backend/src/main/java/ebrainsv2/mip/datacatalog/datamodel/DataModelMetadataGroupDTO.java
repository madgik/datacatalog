package ebrainsv2.mip.datacatalog.datamodel;


import java.util.List;

public record DataModelMetadataGroupDTO(
        String code,
        String label,
        List<CommonDataElementDTO> variables,
        List<DataModelMetadataGroupDTO> groups
) {
    public DataModelMetadataGroupDTO {
        if ((variables == null || variables.isEmpty()) && (groups == null || groups.isEmpty())) {
            throw new InvalidDataModelError("For group '" + code + "', either 'variables' or 'groups' must be present and not empty.");
        }
    }
}
