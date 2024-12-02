package ebrainsv2.mip.datacatalog.utils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.security.core.Authentication;
import org.springframework.security.oauth2.core.oidc.OidcUserInfo;
import org.springframework.security.oauth2.core.oidc.user.DefaultOidcUser;

public class UserActionLogger {

    private final Logger logger;
    private final String username;
    private final String endpoint;

    public UserActionLogger(Authentication authentication, String endpoint) {
        if (authentication != null){
            OidcUserInfo userinfo = ((DefaultOidcUser) authentication.getPrincipal()).getUserInfo();
            this.username = userinfo.getPreferredUsername();
        }
        else this.username = "guest";

        this.endpoint = endpoint;
        this.logger = LoggerFactory.getLogger(UserActionLogger.class);
    }

    private void logUserAction(String message, LogLevel logLevel){
        String logMessage = String.format("User: %s, Endpoint: %s, Info: %s", username, endpoint, message);

        switch (logLevel) {
            case ERROR -> logger.error(logMessage);
            case WARNING -> logger.warn(logMessage);
            case INFO -> logger.info(logMessage);
            case DEBUG -> logger.debug(logMessage);
        }
    }

    public void error(String message) {
        logUserAction(message, LogLevel.ERROR);
    }

    public void warn(String message) {
        logUserAction(message, LogLevel.WARNING);
    }

    public void info(String message) {
        logUserAction(message, LogLevel.INFO);
    }

    public void debug(String message) {
        logUserAction(message, LogLevel.DEBUG);
    }

    private enum LogLevel {
        ERROR, WARNING, INFO, DEBUG
    }
}
