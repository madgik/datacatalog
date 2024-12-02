package ebrainsv2.mip.datacatalog.user;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Scope;
import org.springframework.context.annotation.ScopedProxyMode;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.oauth2.core.oidc.OidcUserInfo;
import org.springframework.security.oauth2.core.oidc.user.DefaultOidcUser;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.stream.Collectors;

@Service
@Scope(value = "session", proxyMode = ScopedProxyMode.TARGET_CLASS)
public class ActiveUserService {

    @Value("${authentication.enabled}")
    private boolean authenticationIsEnabled;

    public ActiveUserService() {}

    /**
     * @return the UserDTO with roles included
     */
    public UserDTO getActiveUser(Authentication authentication) {
        UserDTO activeUserDTO;
        System.out.println("authenticationIsEnabled: " + authenticationIsEnabled + " authentication:" + authentication);

        if (authenticationIsEnabled && authentication != null) {
            // Extract user information from OIDC
            OidcUserInfo userInfo = ((DefaultOidcUser) authentication.getPrincipal()).getUserInfo();
            List<String> roles = authentication.getAuthorities().stream()
                    .filter(auth -> auth instanceof SimpleGrantedAuthority)
                    .map(GrantedAuthority::getAuthority)
                    .collect(Collectors.toList());

            activeUserDTO = new UserDTO(
                    userInfo.getPreferredUsername(),
                    userInfo.getFullName(),
                    userInfo.getEmail(),
                    userInfo.getSubject(),
                    roles
            );

        } else {
            // If Authentication is OFF, create anonymous user with default roles
            activeUserDTO = new UserDTO("anonymous", "anonymous", "anonymous@anonymous.com", "anonymousId", List.of("ROLE_ANONYMOUS"));
        }

        return activeUserDTO;
    }
}
