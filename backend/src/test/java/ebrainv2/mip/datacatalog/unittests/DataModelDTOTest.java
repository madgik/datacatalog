package ebrainv2.mip.datacatalog.unittests;

import ebrainsv2.mip.datacatalog.datamodel.CommonDataElementDTO;
import ebrainsv2.mip.datacatalog.datamodel.DataModelDTO;
import ebrainsv2.mip.datacatalog.datamodel.DataModelMetadataGroupDTO;
import ebrainsv2.mip.datacatalog.datamodel.InvalidDataModelError;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.util.Collections;
import java.util.List;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.*;

class DataModelDTOTest {

    private CommonDataElementDTO validVariable;
    private DataModelMetadataGroupDTO validGroup;

    @BeforeEach
    void setUp() {
        CommonDataElementDTO.EnumerationDTO validEnumeration = new CommonDataElementDTO.EnumerationDTO("enumCode", "enumLabel");
        validVariable = new CommonDataElementDTO("dataset", "label", "description", "text", true, List.of(validEnumeration), 1, 10, "nominal", "methodology", "units");
        validGroup = new DataModelMetadataGroupDTO("groupCode", "groupLabel", List.of(validVariable), Collections.emptyList());
    }

    @Test
    void testSuccessfulDataModelDTOCreation() {
        // Given valid inputs for DataModelDTO
        UUID uuid = UUID.randomUUID();
        String code = "validCode";
        String version = "1.0";
        String label = "Valid Label";
        Boolean longitudinal = false; // For simplicity, start with a non-longitudinal study
        List<CommonDataElementDTO> variables = List.of(validVariable);
        List<DataModelMetadataGroupDTO> groups = List.of(validGroup);
        Boolean released = true;

        // When creating a new DataModelDTO
        assertDoesNotThrow(() -> new DataModelDTO(uuid, code, version, label, longitudinal, variables, groups, released),
                "DataModelDTO should be created successfully without throwing an exception.");
    }

    @Test
    void testValidationForRequiredFields() {
        UUID uuid = UUID.randomUUID();
        Boolean released = true;

        // Test 'code' field by passing null
        Exception codeException = assertThrows(InvalidDataModelError.class, () ->
                new DataModelDTO(uuid, null, "1.0", "Valid Label", false, List.of(validVariable), List.of(validGroup), released)
        );
        assertTrue(codeException.getMessage().contains("code"), "Expected InvalidDataModelError to mention 'code' is required.");

        // Test 'version' field by passing null
        Exception versionException = assertThrows(InvalidDataModelError.class, () ->
                new DataModelDTO(uuid, "validCode", null, "Valid Label", false, List.of(validVariable), List.of(validGroup), released)
        );
        assertTrue(versionException.getMessage().contains("version"), "Expected InvalidDataModelError to mention 'version' is required.");

        // Test 'label' field by passing null
        Exception labelException = assertThrows(InvalidDataModelError.class, () ->
                new DataModelDTO(uuid, "validCode", "1.0", null, false, List.of(validVariable), List.of(validGroup), released)
        );
        assertTrue(labelException.getMessage().contains("label"), "Expected InvalidDataModelError to mention 'label' is required.");

        // Test 'variables' field by passing null
        Exception variablesException = assertThrows(InvalidDataModelError.class, () ->
                new DataModelDTO(uuid, "validCode", "1.0", "Valid Label", false, null, List.of(validGroup), released)
        );
        assertTrue(variablesException.getMessage().contains("variables"), "Expected InvalidDataModelError to mention 'variables' is required.");

        // Test 'variables' field by passing an empty list
        Exception variablesEmptyException = assertThrows(InvalidDataModelError.class, () ->
                new DataModelDTO(uuid, "validCode", "1.0", "Valid Label", false, List.of(), List.of(validGroup), released)
        );
        assertTrue(variablesEmptyException.getMessage().contains("variables"), "Expected InvalidDataModelError to mention 'variables' must not be an empty list.");

        // Test 'groups' field by passing null
        Exception groupsException = assertThrows(InvalidDataModelError.class, () ->
                new DataModelDTO(uuid, "validCode", "1.0", "Valid Label", false, List.of(validVariable), null, released)
        );
        assertTrue(groupsException.getMessage().contains("groups"), "Expected InvalidDataModelError to mention 'groups' is required.");

        // Test 'groups' field by passing an empty list
        Exception groupsEmptyException = assertThrows(InvalidDataModelError.class, () ->
                new DataModelDTO(uuid, "validCode", "1.0", "Valid Label", false, List.of(validVariable), List.of(), released)
        );
        assertTrue(groupsEmptyException.getMessage().contains("groups"), "Expected InvalidDataModelError to mention 'groups' must not be an empty list.");
    }
}

