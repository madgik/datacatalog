package ebrainsv2.mip.datacatalog.datamodel;

import com.fasterxml.jackson.databind.ObjectMapper;
import ebrainsv2.mip.datacatalog.federation.FederationService;
import ebrainsv2.mip.datacatalog.user.ActiveUserService;

import ebrainsv2.mip.datacatalog.utils.UserActionLogger;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.ByteArrayResource;
import org.springframework.http.*;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.util.List;

import static ebrainsv2.mip.datacatalog.datamodel.DataModelConverter.convertExcelToDataModelDTO;
import static org.springframework.http.MediaType.APPLICATION_JSON_VALUE;

@RestController
@RequestMapping(value = "/datamodels", produces = APPLICATION_JSON_VALUE)
public class DataModelAPI {
    private final DataModelService dataModelService;

    @Value("${app.data_quality_tool.json-to-excel-url}")
    private String dqtJsonToExcelUrl;

    @Value("${app.data_quality_tool.excel-to-json-url}")
    private String dqtExcelToJsonUrl;



    public DataModelAPI(DataModelService dataModelService, FederationService federationService, ActiveUserService activeUserService) {
        this.dataModelService = dataModelService;
    }

    @PostMapping("import")
    public ResponseEntity<?> importDataModelViaExcel(
            Authentication authentication,
            @RequestParam("file") MultipartFile file,
            @RequestParam("version") String version,
            @RequestParam("longitudinal") boolean longitudinal) {

        try {
            UserActionLogger logger = new UserActionLogger(authentication, "POST /datamodels/import");

            DataModelDTO dataModelDTO = convertExcelToDataModelDTO(this.dqtExcelToJsonUrl, file, version, longitudinal);
            DataModelDTO createdDataModel = dataModelService.createDataModel(dataModelDTO, logger);
            return new ResponseEntity<>(createdDataModel, HttpStatus.CREATED);
        } catch (Exception e) {
            e.printStackTrace();
            return new ResponseEntity<>(HttpStatus.INTERNAL_SERVER_ERROR);
        }
    }

    @GetMapping("{uuid}/export")
    public ResponseEntity<ByteArrayResource> exportDataModelAsExcel(Authentication authentication, @PathVariable String uuid) {
        try {
            // Fetch your data model by id
            UserActionLogger logger = new UserActionLogger(authentication, "GET /datamodels/" + uuid + "/export");
            DataModelDTO dataModel = dataModelService.getDataModel(authentication, uuid, logger);

            // Convert data model to JSON
            ObjectMapper objectMapper = new ObjectMapper();
            String json = objectMapper.writeValueAsString(dataModel);

            // Set up the request to Flask API
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);

            HttpEntity<String> requestEntity = new HttpEntity<>(json, headers);

            RestTemplate restTemplate = new RestTemplate();
            byte[] excelData = restTemplate.postForObject(this.dqtJsonToExcelUrl, requestEntity, byte[].class);

            // Return the Excel file
            ByteArrayResource resource = new ByteArrayResource(excelData);
            return ResponseEntity.ok()
                    .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=data-model.xlsx")
                    .contentType(MediaType.parseMediaType("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"))
                    .body(resource);
        } catch (Exception e) {
            e.printStackTrace();
            return new ResponseEntity<>(HttpStatus.INTERNAL_SERVER_ERROR);
        }
    }

    @GetMapping()
    public ResponseEntity<List<DataModelDTO>> listDataModels(
            Authentication authentication,
            @RequestParam(name = "released", required = false) Boolean released
    ) {
        UserActionLogger logger = new UserActionLogger(authentication, "GET /datamodels/");
        List<DataModelDTO> dataModels = dataModelService.listDataModels(authentication, released, logger);
        return new ResponseEntity<>(dataModels, HttpStatus.OK);
    }

    @GetMapping("{uuid}")
    public ResponseEntity<DataModelDTO> getDataModel(Authentication authentication, @PathVariable String uuid) {
        UserActionLogger logger = new UserActionLogger(authentication, "GET /datamodels/" + uuid);
        DataModelDTO dataModel = dataModelService.getDataModel(authentication, uuid, logger);
        return new ResponseEntity<>(dataModel, HttpStatus.OK);
    }

    @PreAuthorize("hasAuthority('DC_DOMAIN_EXPERT')")
    @PostMapping()
    public ResponseEntity<DataModelDTO> createDataModel(Authentication authentication, @RequestBody DataModelDTO dataModelDTO) {
        UserActionLogger logger = new UserActionLogger(authentication, "POST /datamodels");
        DataModelDTO createdDataModel = dataModelService.createDataModel(dataModelDTO, logger);
        return new ResponseEntity<>(createdDataModel, HttpStatus.CREATED);
    }

    @PreAuthorize("hasAuthority('DC_DOMAIN_EXPERT')")
    @PutMapping("{uuid}")
    public ResponseEntity<DataModelDTO> updateDataModel(Authentication authentication, @PathVariable String uuid, @RequestBody DataModelDTO dataModelDTO) {
        UserActionLogger logger = new UserActionLogger(authentication, "PUT /datamodels/" + uuid);
        DataModelDTO updatedDataModel = dataModelService.updateDataModel(uuid, dataModelDTO, logger);
        return updatedDataModel != null ? new ResponseEntity<>(updatedDataModel, HttpStatus.OK)
                : new ResponseEntity<>(HttpStatus.NOT_FOUND);
    }

    @PreAuthorize("hasAuthority('DC_DOMAIN_EXPERT')")
    @PutMapping("{uuid}/excel")
    public ResponseEntity<DataModelDTO> updateDataModelviaExcel(
            Authentication authentication,
            @PathVariable String uuid,
            @RequestParam("file") MultipartFile file,
            @RequestParam("version") String version,
            @RequestParam("longitudinal") boolean longitudinal) throws IOException {
        UserActionLogger logger = new UserActionLogger(authentication, "PUT /datamodels/" + uuid + "/excel");
        DataModelDTO dataModelDTO = convertExcelToDataModelDTO(this.dqtExcelToJsonUrl, file, version, longitudinal);
        DataModelDTO updatedDataModel = dataModelService.updateDataModel(uuid, dataModelDTO, logger);
        return updatedDataModel != null ? new ResponseEntity<>(updatedDataModel, HttpStatus.OK)
                : new ResponseEntity<>(HttpStatus.NOT_FOUND);
    }

    @PreAuthorize("hasAuthority('DC_DOMAIN_EXPERT')")
    @DeleteMapping("{uuid}")
    public ResponseEntity<Void> deleteDataModel(Authentication authentication, @PathVariable String uuid) {
        UserActionLogger logger = new UserActionLogger(authentication, "DELETE /datamodels/" + uuid);
        dataModelService.deleteDataModel(uuid, logger);
        return new ResponseEntity<>(HttpStatus.NO_CONTENT);
    }

    @PreAuthorize("hasAuthority('DC_DOMAIN_EXPERT')")
    @PostMapping("{uuid}/release")
    public ResponseEntity<Void> releaseDataModel(Authentication authentication, @PathVariable String uuid) {
        UserActionLogger logger = new UserActionLogger(authentication, "POST /datamodels/" + uuid + "/release");
        dataModelService.releaseDataModel(uuid, logger);
        return new ResponseEntity<>(HttpStatus.OK);
    }

}
