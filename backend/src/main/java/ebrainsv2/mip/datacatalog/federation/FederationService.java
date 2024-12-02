package ebrainsv2.mip.datacatalog.federation;

import ebrainsv2.mip.datacatalog.datamodel.DataModelDAO;
import ebrainsv2.mip.datacatalog.datamodel.DataModelRepository;
import ebrainsv2.mip.datacatalog.utils.Exceptions.DataModelNotFoundException;
import ebrainsv2.mip.datacatalog.utils.UserActionLogger;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

import java.util.UUID;
import java.util.stream.Collectors;

@Service
public class FederationService {
    private final FederationRepository federationRepository;
    private final DataModelRepository dataModelRepository;
    public FederationService(FederationRepository federationRepository, DataModelRepository dataModelRepository) {
        this.federationRepository = federationRepository;
        this.dataModelRepository = dataModelRepository;
    }

    public FederationDTO createFederation(FederationDTO federationDTO, UserActionLogger logger) {
        logger.info("Creating Federation with code: " + federationDTO.code());
        FederationDAO federationDAO = FederationConverter.dtoToDao(federationDTO);

        // Convert UUIDs to Strings and fetch DataModel entities
        List<String> dataModelIdsAsStrings = federationDTO.dataModelIds().stream()
                .map(UUID::toString) // Convert UUID to String
                .collect(Collectors.toList());
        List<DataModelDAO> dataModelEntities = (List<DataModelDAO>) dataModelRepository.findAllById(dataModelIdsAsStrings);

        // Validate that all provided UUIDs exist in the database
        validateDataModelIds(dataModelIdsAsStrings, dataModelEntities, federationDTO.code(), logger);

        federationDAO.setDataModels(dataModelEntities);
        FederationDAO savedFederation = federationRepository.save(federationDAO);
        logger.info("Federation created successfully with code: " + federationDTO.code());
        return FederationConverter.daoToDto(savedFederation);
    }

    @Transactional
    public FederationDTO updateFederation(String code, FederationDTO federationDTO, UserActionLogger logger) {
        logger.info("Updating Federation with code: " + code);

        // Fetch the existing Federation
        FederationDAO existingFederation = federationRepository.findByCode(code)
                .orElseThrow(() -> new DataModelNotFoundException("Federation not found with code: " + code));

        // Update basic attributes
        existingFederation.setTitle(federationDTO.title());
        existingFederation.setDescription(federationDTO.description());
        existingFederation.setUrl(federationDTO.url());
        existingFederation.setRecords(federationDTO.records());
        existingFederation.setInstitutions(federationDTO.institutions());

        // Handle DataModel IDs
        List<String> dataModelIdsAsStrings = federationDTO.dataModelIds()
                .stream()
                .map(UUID::toString)
                .collect(Collectors.toList());

        List<DataModelDAO> dataModelEntities = (List<DataModelDAO>) dataModelRepository.findAllById(dataModelIdsAsStrings);

        validateDataModelIds(dataModelIdsAsStrings, dataModelEntities, code, logger);

        existingFederation.setDataModels(dataModelEntities);

        // Save and log the update
        FederationDAO updatedFederation = federationRepository.save(existingFederation);
        logger.info("Federation updated successfully with code: " + code);

        // Convert to DTO and return
        return FederationConverter.daoToDto(updatedFederation);
    }


    /**
     * Helper method to validate that all provided UUIDs exist in the database.
     */
    private void validateDataModelIds(List<String> providedIds, List<DataModelDAO> foundEntities, String federationCode, UserActionLogger logger) {
        // Convert UUIDs of found entities to Strings
        List<String> foundIds = foundEntities.stream()
                .map(dataModelDAO -> dataModelDAO.getUuid().toString())
                .toList();

        // Check for missing IDs
        List<String> missingIds = providedIds.stream()
                .filter(id -> !foundIds.contains(id))
                .toList();

        // Log and throw exception for missing IDs
        if (!missingIds.isEmpty()) {
            logger.error("Invalid DataModel UUIDs for Federation " + federationCode + ": " + missingIds);
            throw new DataModelNotFoundException("The following DataModel UUIDs do not exist: " + missingIds);
        }

        // Check if all found entities are released
        List<String> unreleasedIds = foundEntities.stream()
                .filter(dataModelDAO -> Boolean.FALSE.equals(dataModelDAO.getReleased()))
                .map(dataModelDAO -> dataModelDAO.getUuid().toString())
                .toList();

        // Log and throw exception for unreleased data models
        if (!unreleasedIds.isEmpty()) {
            logger.error("All DataModels added to Federation " + federationCode + " must be released. Unreleased DataModel UUIDs: " + unreleasedIds);
            throw new IllegalStateException("The following DataModel UUIDs are not released: " + unreleasedIds);
        }
    }


    public FederationDTO getFederationByCode(String code, UserActionLogger logger) {
        logger.info("Retrieving Federation with code: " + code);
        FederationDAO federationDAO = federationRepository.findByCode(code)
                .orElseThrow(() -> {
                    logger.error("Federation not found with code: " + code);
                    return new DataModelNotFoundException("Federation not found with code: " + code);
                });
        FederationDTO federationDTO = FederationConverter.daoToDto(federationDAO);
        logger.info("Federation with code: " + code + " retrieved successfully.");
        return federationDTO;
    }

    @Transactional
    public void deleteFederation(String code, UserActionLogger logger) {
        logger.info("Deleting Federation with code: " + code);
        if (!federationRepository.existsByCode(code)) {
            logger.error("Federation with code: " + code + " does not exist and cannot be deleted.");
            throw new DataModelNotFoundException("Federation with code: " + code + " not found.");
        }
        federationRepository.deleteByCode(code);
        logger.info("Federation with code: " + code + " deleted successfully.");
    }

    public List<FederationDTO> getAllFederations(UserActionLogger logger) {
        logger.info("Retrieving all Federation entries");
        List<FederationDAO> federationDAOList = (List<FederationDAO>) federationRepository.findAll();
        List<FederationDTO> federationDTOList = federationDAOList.stream()
                .map(FederationConverter::daoToDto)
                .toList();
        logger.info("All Federation entries retrieved successfully.");
        return federationDTOList;
    }

}
