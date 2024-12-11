package ebrainsv2.mip.datacatalog.datamodel;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.core.io.ByteArrayResource;
import org.springframework.core.io.FileSystemResource;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.multipart.MultipartFile;

import java.io.File;
import java.io.IOException;
import java.util.List;
import java.util.Map;

public class DataModelConverter {

    private static final ObjectMapper objectMapper = new ObjectMapper();

    public static ByteArrayResource convertDataModelDTOToExcel(String dqtJsonToExcelUrl, DataModelDTO dataModel) throws IOException {

        ObjectMapper objectMapper = new ObjectMapper();
        String json = objectMapper.writeValueAsString(dataModel);

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);

        HttpEntity<String> requestEntity = new HttpEntity<>(json, headers);

        RestTemplate restTemplate = new RestTemplate();
        byte[] excelData = restTemplate.postForObject(dqtJsonToExcelUrl, requestEntity, byte[].class);

        return new ByteArrayResource(excelData);
    }

    public static DataModelDTO convertExcelToDataModelDTO(String dqtExcelToJsonUrl,
                                                          MultipartFile file,
                                                          String version,
                                                          boolean longitudinal) throws IOException {
        // Convert MultipartFile to File
        File convFile = new File(System.getProperty("java.io.tmpdir") + "/" + file.getOriginalFilename());
        file.transferTo(convFile);

        // Setup the request to Flask API
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.MULTIPART_FORM_DATA);

        MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
        body.add("file", new FileSystemResource(convFile));

        HttpEntity<MultiValueMap<String, Object>> requestEntity = new HttpEntity<>(body, headers);

        RestTemplate restTemplate = new RestTemplate();
        ResponseEntity<String> response = restTemplate.postForEntity(dqtExcelToJsonUrl, requestEntity, String.class);

        // Convert JSON response to a Map and add "longitudinal" and "version" fields
        ObjectMapper objectMapper = new ObjectMapper();
        Map dataMap = objectMapper.readValue(response.getBody(), Map.class);
        dataMap.put("longitudinal", longitudinal);
        dataMap.put("version", version);

        // Convert the modified Map back to JSON and map it to DataModelDTO
        return objectMapper.convertValue(dataMap, DataModelDTO.class);
    }
    
    
    public static DataModelDTO convertToDataModelDTO(DataModelDAO dataModelDAO) {
        try {
            List<CommonDataElementDTO> variables = objectMapper.readValue(
                    dataModelDAO.getVariables(), new TypeReference<>() {
                    }
            );
            List<DataModelMetadataGroupDTO> groups = objectMapper.readValue(
                    dataModelDAO.getGroups(), new TypeReference<>() {
                    }
            );

            return new DataModelDTO(
                    dataModelDAO.getUuid(),
                    dataModelDAO.getCode(),
                    dataModelDAO.getVersion(),
                    dataModelDAO.getLabel(),
                    dataModelDAO.getLongitudinal(),
                    variables,
                    groups,
                    dataModelDAO.getReleased()
            );
        } catch (JsonProcessingException e) {
            throw new RuntimeException("Error in deserializing data from DataModelDAO: " + e.getMessage(), e);
        }
    }

    public static DataModelDAO dtoToDao(DataModelDTO dataModelDTO) {
        DataModelDAO dataModelDAO = new DataModelDAO();
        try {
            String variablesJson = objectMapper.writeValueAsString(dataModelDTO.variables());
            String groupsJson = objectMapper.writeValueAsString(dataModelDTO.groups());

            dataModelDAO.setUuid(dataModelDTO.uuid());
            dataModelDAO.setCode(dataModelDTO.code());
            dataModelDAO.setVersion(dataModelDTO.version());
            dataModelDAO.setLabel(dataModelDTO.label());
            dataModelDAO.setLongitudinal(Boolean.parseBoolean(String.valueOf(dataModelDTO.longitudinal())));
            dataModelDAO.setVariables(variablesJson);
            dataModelDAO.setGroups(groupsJson);
            dataModelDAO.setReleased(dataModelDTO.released() != null && dataModelDTO.released());

            return dataModelDAO;
        } catch (JsonProcessingException e) {
            throw new RuntimeException("Error in serializing data to DataModelDAO: " + e.getMessage(), e);
        }
    }

}
