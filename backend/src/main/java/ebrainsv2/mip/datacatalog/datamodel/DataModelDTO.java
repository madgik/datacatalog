package ebrainsv2.mip.datacatalog.datamodel;

import java.util.List;
import java.util.UUID;

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
}

