package ebrainsv2.mip.datacatalog.datamodel;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.client.RestTemplate;

import java.io.IOException;

public class DataModelValidator {
    public static String validateJson(String dqtValidateJsonUrl, DataModelDTO dataModelDTO) throws IOException {
        // Serialize DataModelDTO to JSON
        ObjectMapper objectMapper = new ObjectMapper();
        String json = objectMapper.writeValueAsString(dataModelDTO);

        // Setup the request to Flask API
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);

        HttpEntity<String> requestEntity = new HttpEntity<>(json, headers);

        RestTemplate restTemplate = new RestTemplate();
        try {
            ResponseEntity<String> response = restTemplate.postForEntity(dqtValidateJsonUrl, requestEntity, String.class);
            if (response.getStatusCode().is2xxSuccessful()) {
                System.out.println("Validation success: " + response.getBody());
                return response.getBody();
            } else {
                System.err.println("Validation failed with status: " + response.getStatusCode() + ", Body: " + response.getBody());
                throw new RuntimeException("JSON validation failed: " + response.getBody());
            }
        } catch (Exception e) {
            System.err.println("Unexpected error occurred while validating JSON: " + e.getMessage());
            throw e;
        }
    }

}
