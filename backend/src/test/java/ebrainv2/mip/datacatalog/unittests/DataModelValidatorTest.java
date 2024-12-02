package ebrainv2.mip.datacatalog.unittests;

import ebrainsv2.mip.datacatalog.datamodel.CommonDataElementDTO;
import ebrainsv2.mip.datacatalog.datamodel.DataModelMetadataGroupDTO;
import ebrainsv2.mip.datacatalog.datamodel.InvalidDataModelError;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.util.Collections;
import java.util.List;

import static ebrainsv2.mip.datacatalog.datamodel.DataModelValidator.containsRequiredDataset;
import static ebrainsv2.mip.datacatalog.datamodel.DataModelValidator.validateLongitudinalElements;
import static org.junit.jupiter.api.Assertions.*;

class DataModelValidatorTest {

    private DataModelMetadataGroupDTO validGroup;

    @BeforeEach
    void setUp() {
        CommonDataElementDTO validVariable = new CommonDataElementDTO("dataset", "label", "description", "text", true, List.of(new CommonDataElementDTO.EnumerationDTO("enumCode", "enumLabel")), 1, 10, "nominal", "methodology", "units");
        validGroup = new DataModelMetadataGroupDTO("groupCode", "groupLabel", List.of(validVariable), Collections.emptyList());
    }

    @Test
    void testValidationForRequiredDataset() {
        // Create a variable that is not marked as the required dataset
        CommonDataElementDTO nonDatasetVariable = new CommonDataElementDTO("nonDatasetCode", "label", "description", "text", false, List.of(), 1, 10, "nominal", "methodology", "units");
        // Create a group without the required dataset
        DataModelMetadataGroupDTO groupWithoutRequiredDataset = new DataModelMetadataGroupDTO("groupCode", "groupLabel", List.of(nonDatasetVariable), List.of());
        assertFalse(containsRequiredDataset(List.of(nonDatasetVariable), List.of(groupWithoutRequiredDataset)));
    }
    @Test
    void testValidationForLongitudinalStudyElements() {
        CommonDataElementDTO subjectIdVariable = new CommonDataElementDTO("subjectid", "Subject ID", "description", "text", false, List.of(), null, null, "nominal", "methodology", "units");
        CommonDataElementDTO.EnumerationDTO validEnumeration = new CommonDataElementDTO.EnumerationDTO("enumCode", "enumLabel");

        CommonDataElementDTO invalidVisitIdVariable = new CommonDataElementDTO("visitid", "Visit ID", "description", "invalid_sql_type", true, List.of(validEnumeration), null, null, "nominal", "methodology", "units"); // Missing enumerations

        // Test missing 'subjectid'
        Exception subjectIdException = assertThrows(InvalidDataModelError.class, () ->
                validateLongitudinalElements(List.of(invalidVisitIdVariable), List.of(validGroup)),
                "Expected InvalidDataModelError to mention missing 'subjectid' for longitudinal study."
        );
        assertTrue(subjectIdException.getMessage().contains("subjectid"), "Expected exception message to mention missing 'subjectid'.");

        // Test invalid 'visitid'
        Exception visitIdException = assertThrows(InvalidDataModelError.class, () ->
                validateLongitudinalElements(List.of(subjectIdVariable, invalidVisitIdVariable), List.of(validGroup)),
                "Expected InvalidDataModelError to mention invalid 'visitid' for longitudinal study."
        );
        assertTrue(visitIdException.getMessage().contains("visitid"), "Expected exception message to mention invalid 'visitid'.");
    }

}

