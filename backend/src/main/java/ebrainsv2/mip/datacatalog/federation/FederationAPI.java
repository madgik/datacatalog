package ebrainsv2.mip.datacatalog.federation;

import ebrainsv2.mip.datacatalog.datamodel.DataModelService;
import ebrainsv2.mip.datacatalog.user.ActiveUserService;
import ebrainsv2.mip.datacatalog.utils.UserActionLogger;
import org.springframework.http.*;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

import java.util.List;

import static org.springframework.http.MediaType.APPLICATION_JSON_VALUE;

@RestController
@RequestMapping(value = "/federations", produces = APPLICATION_JSON_VALUE)
public class FederationAPI {
    private final FederationService federationService;


    public FederationAPI(DataModelService dataModelService, FederationService federationService, ActiveUserService activeUserService) {
        this.federationService = federationService;
    }
    

    @PreAuthorize("hasAuthority('DC_ADMIN')")
    @PostMapping()
    public ResponseEntity<FederationDTO> createFederation(Authentication authentication, @RequestBody FederationDTO federationDTO) {
        UserActionLogger logger = new UserActionLogger(authentication, "POST /federations");
        FederationDTO createdFederation = federationService.createFederation(federationDTO, logger);
        return new ResponseEntity<>(createdFederation, HttpStatus.CREATED);
    }

    @GetMapping("/{code}")  // Updated from dataModel to code
    public ResponseEntity<FederationDTO> getFederation(Authentication authentication, @PathVariable String code) {
        UserActionLogger logger = new UserActionLogger(authentication, "GET /federations/" + code);
        FederationDTO dataModelInfo = federationService.getFederationByCode(code, logger);  // Use code instead of dataModel
        return new ResponseEntity<>(dataModelInfo, HttpStatus.OK);
    }

    @PreAuthorize("hasAuthority('DC_ADMIN')")
    @PutMapping("/{code}")  // Updated from dataModel to code
    public ResponseEntity<FederationDTO> updateFederation(Authentication authentication, @PathVariable String code, @RequestBody FederationDTO federationDTO) {
        UserActionLogger logger = new UserActionLogger(authentication, "PUT /federations/" + code);
        FederationDTO updatedFederation = federationService.updateFederation(code, federationDTO, logger);  // Use code instead of dataModel
        return new ResponseEntity<>(updatedFederation, HttpStatus.OK);
    }

    @PreAuthorize("hasAuthority('DC_ADMIN')")
    @DeleteMapping("/{code}")  // Updated from dataModel to code
    public ResponseEntity<Void> deleteFederation(Authentication authentication, @PathVariable String code) {
        UserActionLogger logger = new UserActionLogger(authentication, "DELETE /federations/" + code);
        federationService.deleteFederation(code, logger);  // Use code instead of dataModel
        return new ResponseEntity<>(HttpStatus.NO_CONTENT);
    }

    @GetMapping()
    public ResponseEntity<List<FederationDTO>> getAllFederations(Authentication authentication) {
        UserActionLogger logger = new UserActionLogger(authentication, "GET /federations");
        List<FederationDTO> allFederations = federationService.getAllFederations(logger);
        return new ResponseEntity<>(allFederations, HttpStatus.OK);
    }
}
