package ebrainsv2.mip.datacatalog.federation;

import java.util.List;
import java.util.UUID;

public record FederationDTO(
        String code,
        String title,
        String url,
        String description,
        int records,
        int institutions,
        List<UUID> dataModelIds // Accept only UUIDs for data models
) {
}
