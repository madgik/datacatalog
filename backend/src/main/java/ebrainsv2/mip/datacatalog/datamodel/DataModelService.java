package ebrainsv2.mip.datacatalog.datamodel;

import ebrainsv2.mip.datacatalog.utils.Exceptions.BadRequestException;
import ebrainsv2.mip.datacatalog.utils.Exceptions.DataModelNotFoundException;
import ebrainsv2.mip.datacatalog.utils.UserActionLogger;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.security.core.Authentication;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.stream.Collectors;

import static ebrainsv2.mip.datacatalog.datamodel.DataModelConverter.dtoToDao;
import static ebrainsv2.mip.datacatalog.datamodel.DataModelConverter.convertToDataModelDTO;

@Service
public class DataModelService {
    @Value("${authentication.domain_expert}")
    private String domain_expert;
    
    private final DataModelRepository dataModelRepository;

    public DataModelService(DataModelRepository dataModelRepository) {
        this.dataModelRepository = dataModelRepository;
    }

    public List<DataModelDTO> listDataModels(Authentication authentication, Boolean released, UserActionLogger logger) {
        logger.info("Listing data models. Released filter: " + released);
        List<DataModelDAO> dataModelDAOS;

        boolean isDomainExpert = checkIsDomainExpert(authentication);
        if (authentication == null)
        {
            logger.info("Fetching all data models for domain experts.");
            dataModelDAOS = released == null ?
                    (List<DataModelDAO>) dataModelRepository.findAll() :
                    dataModelRepository.findByReleased(released);
        }
        else {
            if (!isDomainExpert) {
                logger.info("Fetching only released data models for non-domain experts or unauthenticated users.");
                dataModelDAOS = dataModelRepository.findByReleased(true);
            } else {
                logger.info("Fetching all data models for domain experts.");
                dataModelDAOS = released == null ?
                        (List<DataModelDAO>) dataModelRepository.findAll() :
                        dataModelRepository.findByReleased(released);
            }
        }

        List<DataModelDTO> dataModels = dataModelDAOS.stream()
                .map(DataModelConverter::convertToDataModelDTO)
                .collect(Collectors.toList());
        logger.info("Successfully listed data models. Count: " + dataModels.size());
        return dataModels;
    }

    public DataModelDTO getDataModel(Authentication authentication, String uuid, UserActionLogger logger) {
        logger.info("Retrieving data model with UUID: " + uuid);
        DataModelDAO dataModelDAO = retrieveDataModelDAO(uuid, logger);

        boolean isDomainExpert = checkIsDomainExpert(authentication);

        if (isDomainExpert || dataModelDAO.getReleased()) {
            logger.info(String.format("Data model %s accessed by %s", uuid, isDomainExpert ? "domain expert" : "non-domain expert"));
            return convertToDataModelDTO(dataModelDAO);
        } else {
            String errorMessage = "Access denied for data model with UUID: " + uuid + ". Not released.";
            logger.error(errorMessage);
            throw new BadRequestException(errorMessage);
        }
    }



    public DataModelDTO createDataModel(DataModelDTO dataModelDTO, UserActionLogger logger) {
        logger.info("Creating new data model with code: " + dataModelDTO.code() + " and version: " + dataModelDTO.version());
        Optional<DataModelDAO> existingDataModel = dataModelRepository.findByCodeAndVersion(dataModelDTO.code(), dataModelDTO.version());

        if (existingDataModel.isPresent()) {
            String errorMessage = "Data model with code: " + dataModelDTO.code() + " and version: " + dataModelDTO.version() + " already exists.";
            logger.error(errorMessage);
            throw new DataIntegrityViolationException(errorMessage);
        }


        DataModelDAO dataModelDAO = dtoToDao(dataModelDTO);
        DataModelDAO savedDataModel = dataModelRepository.save(dataModelDAO);
        logger.info("Data model created with UUID: " + savedDataModel.getUuid());
        return convertToDataModelDTO(savedDataModel);
    }


    public DataModelDTO updateDataModel(String uuid, DataModelDTO dataModelDTO, UserActionLogger logger) {
        logger.info("Updating data model with UUID: " + uuid);
        UUID id = UUID.fromString(uuid);
        DataModelDAO existingDataModel = retrieveDataModelDAO(uuid, logger);

        if (existingDataModel.getReleased()) {
            String errorMessage = "Cannot update released data model with UUID: " + uuid;
            logger.error(errorMessage);
            throw new DataIntegrityViolationException(errorMessage);
        }

        DataModelDAO updatedDataModelDAO = dtoToDao(dataModelDTO);
        updatedDataModelDAO.setUuid(id);
        dataModelRepository.save(updatedDataModelDAO);
        logger.info("Data model with UUID: " + uuid + " updated successfully");
        return convertToDataModelDTO(updatedDataModelDAO);
    }


    @Transactional
    public void deleteDataModel(String uuid, UserActionLogger logger) {
        logger.info("Deleting data model with UUID: " + uuid);
        UUID id = UUID.fromString(uuid);
        DataModelDAO existingDataModel = retrieveDataModelDAO(uuid, logger);

        if (existingDataModel.getReleased()) {
            String errorMessage = "Cannot delete released data model with UUID: " + uuid;
            logger.error(errorMessage);
            throw new DataIntegrityViolationException(errorMessage);
        }

        dataModelRepository.deleteByUuid(id);
        logger.info("Data model with UUID: " + uuid + " deleted successfully");
    }


    public void releaseDataModel(String uuid, UserActionLogger logger) {
        logger.info("Initiating release of data model with UUID: " + uuid);
        DataModelDAO existingDataModel = retrieveDataModelDAO(uuid, logger);

        if (existingDataModel.getReleased()) {
            String errorMessage = "Data model with UUID: " + uuid + " is already released.";
            logger.error(errorMessage);
            throw new DataIntegrityViolationException(errorMessage);
        }

        existingDataModel.setReleased(true);
        dataModelRepository.save(existingDataModel);
        logger.info("Data model with UUID: " + uuid + " successfully released.");
    }


    private boolean checkIsDomainExpert(Authentication authentication){
        return authentication != null && authentication.getAuthorities().stream()
                .anyMatch(grantedAuthority -> grantedAuthority.getAuthority().equals(domain_expert));
    }

    private DataModelDAO retrieveDataModelDAO(String uuid, UserActionLogger logger) {
        logger.info("Retrieving data model DAO for UUID: " + uuid);
        return Optional.ofNullable(dataModelRepository.findByUuid(UUID.fromString(uuid)))
                .orElseThrow(() -> {
                    String errorMessage = "Data model with UUID: " + uuid + " not found.";
                    logger.error(errorMessage);
                    return new DataModelNotFoundException(errorMessage);
                });
    }

}
