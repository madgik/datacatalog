package ebrainsv2.mip.datacatalog.user;

import java.util.List;

public record UserDTO(String username, String fullname, String email, String subjectId, List<String> roles){

}