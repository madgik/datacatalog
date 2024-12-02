package ebrainsv2.mip.datacatalog.configurations;

import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.method.configuration.EnableMethodSecurity;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.annotation.web.configurers.AbstractHttpConfigurer;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.authority.mapping.GrantedAuthoritiesMapper;
import org.springframework.security.oauth2.client.OAuth2AuthorizedClient;
import org.springframework.security.oauth2.client.OAuth2AuthorizedClientService;
import org.springframework.security.oauth2.client.authentication.OAuth2AuthenticationToken;
import org.springframework.security.oauth2.client.oidc.web.logout.OidcClientInitiatedLogoutSuccessHandler;
import org.springframework.security.oauth2.client.registration.ClientRegistration;
import org.springframework.security.oauth2.client.registration.ClientRegistrationRepository;
import org.springframework.security.oauth2.client.registration.InMemoryClientRegistrationRepository;
import org.springframework.security.oauth2.core.AuthorizationGrantType;
import org.springframework.security.oauth2.core.oidc.user.OidcUserAuthority;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.stereotype.Component;

import java.util.*;
import java.util.stream.Collectors;

@Configuration
@EnableWebSecurity
@EnableMethodSecurity
public class SecurityConfiguration {

    @Value("${app.frontend.auth-callback-url}")
    private String authCallbackUrl;

    @Value("${app.frontend.base-url}")
    private String frontendBaseUrl;

    @Value("${authentication.enabled}")
    private boolean authenticationEnabled;

    @Bean
    @ConditionalOnProperty(prefix = "authentication", name = "enabled", havingValue = "0")
    public ClientRegistrationRepository clientRegistrationRepository() {
        ClientRegistration dummyRegistration = ClientRegistration.withRegistrationId("dummy")
                .clientId("google-client-id")
                .clientSecret("google-client-secret")
                .authorizationGrantType(AuthorizationGrantType.AUTHORIZATION_CODE)
                .redirectUri("{baseUrl}/login/oauth2/code/{registrationId}")
                .scope("openid")
                .authorizationUri("https://accounts.google.com/o/oauth2/v2/auth")
                .tokenUri("https://www.googleapis.com/oauth2/v4/token")
                .userInfoUri("https://www.googleapis.com/oauth2/v3/userinfo")
                .jwkSetUri("https://www.googleapis.com/oauth2/v3/certs")
                .build();
        return new InMemoryClientRegistrationRepository(dummyRegistration);
    }

    @Bean
    public SecurityFilterChain clientSecurityFilterChain(HttpSecurity http, ClientRegistrationRepository clientRegistrationRepo,
                                                         OAuth2AuthorizedClientService authorizedClientService) throws Exception {

        if (authenticationEnabled) {
            http
            .authorizeHttpRequests(auth -> auth
                    .anyRequest().permitAll() // Allow access to any endpoint unless restricted by @PreAuthorize
            )
            .oauth2Login(oauth -> oauth
                    .defaultSuccessUrl(this.authCallbackUrl, true)
                    .successHandler((request, response, authentication) -> {
                        OAuth2AuthenticationToken oauthToken = (OAuth2AuthenticationToken) authentication;

                        OAuth2AuthorizedClient client = authorizedClientService.loadAuthorizedClient(
                                oauthToken.getAuthorizedClientRegistrationId(),
                                oauthToken.getName()
                        );

                        String token = client.getAccessToken().getTokenValue();
                        System.out.println("Authentication successful. Redirecting to Angular auth-callback with token: " + token);

                        response.sendRedirect(this.authCallbackUrl + "?token=" + token);
                    })
            )
            .logout(logout -> {
                OidcClientInitiatedLogoutSuccessHandler successHandler = new OidcClientInitiatedLogoutSuccessHandler(clientRegistrationRepo);
                successHandler.setPostLogoutRedirectUri(this.frontendBaseUrl);
                logout.logoutSuccessHandler(successHandler);
            })
            .csrf(AbstractHttpConfigurer::disable); // Ensure CSRF protection as per requirements
        } else {
            http
                    .authorizeHttpRequests(auth -> auth
                            .anyRequest().permitAll()
                    )
                    .csrf(AbstractHttpConfigurer::disable);
        }
        return http.build();
    }

    @Component
    @RequiredArgsConstructor
    static class GrantedAuthoritiesMapperImpl implements GrantedAuthoritiesMapper {
        private static Collection<GrantedAuthority> extractAuthorities(Map<String, Object> claims) {
            return ((Collection<String>) claims.get("authorities")).stream()
                    .map(SimpleGrantedAuthority::new)
                    .collect(Collectors.toList());
        }

        @Override
        public Collection<? extends GrantedAuthority> mapAuthorities(Collection<? extends GrantedAuthority> authorities) {
            Set<GrantedAuthority> mappedAuthorities = new HashSet<>();

            authorities.forEach(authority -> {
                if (authority instanceof OidcUserAuthority oidcUserAuthority) {
                    mappedAuthorities.addAll(extractAuthorities(oidcUserAuthority.getIdToken().getClaims()));
                }
            });

            return mappedAuthorities;
        }
    }
}
