package ebrainsv2.mip.datacatalog.user;

import ebrainsv2.mip.datacatalog.utils.UserActionLogger;
import org.springframework.http.*;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

import static org.springframework.http.MediaType.APPLICATION_JSON_VALUE;

@RestController
@RequestMapping(value = "/user", produces = APPLICATION_JSON_VALUE)
public class UserAPI {
    private final ActiveUserService activeUserService;


    public UserAPI(ActiveUserService activeUserService) {
        this.activeUserService = activeUserService;
    }


    @GetMapping()
    public ResponseEntity<UserDTO> getTheActiveUser(Authentication authentication) {
        UserDTO activeUser = activeUserService.getActiveUser(authentication);
        UserActionLogger logger = new UserActionLogger(authentication, "(GET) /activeUser");
        logger.info("User details returned.");
        return ResponseEntity.ok(activeUser);
    }
}
