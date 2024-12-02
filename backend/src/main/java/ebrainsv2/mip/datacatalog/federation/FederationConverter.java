package ebrainsv2.mip.datacatalog.federation;

import ebrainsv2.mip.datacatalog.datamodel.DataModelDAO;
import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

public class FederationConverter {

    // Convert FederationDAO to FederationDTO with data model UUIDs only
    public static FederationDTO daoToDto(FederationDAO federationDAO) {
        List<UUID> dataModelIds = federationDAO.getDataModels().stream()
                .map(DataModelDAO::getUuid)
                .collect(Collectors.toList());
        return new FederationDTO(
                federationDAO.getCode(),
                federationDAO.getTitle(),
                federationDAO.getUrl(),
                federationDAO.getDescription(),
                federationDAO.getRecords(),
                federationDAO.getInstitutions(),
                dataModelIds
        );
    }

    // Convert FederationDTO to FederationDAO
    public static FederationDAO dtoToDao(FederationDTO federationDTO) {
        FederationDAO federationDAO = new FederationDAO();
        federationDAO.setCode(federationDTO.code());
        federationDAO.setTitle(federationDTO.title());
        federationDAO.setDescription(federationDTO.description());
        federationDAO.setUrl(federationDTO.url());
        federationDAO.setRecords(federationDTO.records());
        federationDAO.setInstitutions(federationDTO.institutions());
        // Note: DataModel associations are set in the service layer, not here
        return federationDAO;
    }
}
