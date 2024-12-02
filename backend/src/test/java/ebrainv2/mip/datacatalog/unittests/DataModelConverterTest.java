package ebrainv2.mip.datacatalog.unittests;

import com.fasterxml.jackson.databind.ObjectMapper;
import ebrainsv2.mip.datacatalog.datamodel.DataModelConverter;
import ebrainsv2.mip.datacatalog.datamodel.DataModelDAO;
import ebrainsv2.mip.datacatalog.datamodel.DataModelDTO;
import ebrainsv2.mip.datacatalog.datamodel.DataModelMetadataGroupDTO;
import ebrainv2.mip.datacatalog.TestUtil;
import org.junit.jupiter.api.Test;

import java.io.IOException;

import static org.junit.jupiter.api.Assertions.*;

public class DataModelConverterTest {

    private final ObjectMapper objectMapper = new ObjectMapper();

    @Test
    void testConvertJsonToDataModelDTO() throws IOException {
        String jsonFilePath = "src/test/resources/MinimalDataModelExample.json";
        String jsonContent = TestUtil.readJsonFileAsString(jsonFilePath);

        DataModelDTO dataModelDTO = objectMapper.readValue(jsonContent, DataModelDTO.class);
        DataModelDAO dataModelDAO = DataModelConverter.dtoToDao(dataModelDTO);

        // Perform assertions to validate the conversion
        assertNotNull(dataModelDAO, "DataModelDAO should not be null.");
        assertNotNull(dataModelDTO, "DataModelDTO should not be null.");
        assertEquals(dataModelDTO.code(), dataModelDAO.getCode(), "Code should match.");
        assertEquals(dataModelDTO.version(), dataModelDAO.getVersion(), "Version should match.");
        assertEquals(dataModelDTO.label(), dataModelDAO.getLabel(), "Label should match.");

        // Assertions for variables
        assertFalse(dataModelDAO.getVariables().isEmpty(), "Variables should not be empty.");
        assertFalse(dataModelDTO.variables().isEmpty(), "Variables should not be empty.");

        assertEquals(objectMapper.writeValueAsString(dataModelDTO.variables()), dataModelDAO.getVariables(), "variables should match.");
        assertEquals(objectMapper.writeValueAsString(dataModelDTO.groups()), dataModelDAO.getGroups(), "groups should match.");

        // Assertions for groups
        assertFalse(dataModelDTO.groups().isEmpty(), "Groups should not be empty.");
        DataModelMetadataGroupDTO group = dataModelDTO.groups().get(0);
        assertEquals("example_group", group.code(), "Group code should match.");

        // Assertions for nested groups
        assertFalse(group.groups().isEmpty(), "Nested groups should not be empty.");
        DataModelMetadataGroupDTO nestedGroup = group.groups().get(0);
        assertEquals("nested_group", nestedGroup.code(), "Nested group code should match.");
    }
}
