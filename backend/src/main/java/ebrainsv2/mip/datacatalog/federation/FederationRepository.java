package ebrainsv2.mip.datacatalog.federation;

import org.springframework.data.repository.CrudRepository;
import org.springframework.data.rest.core.annotation.RestResource;

import java.util.Optional;

@RestResource(exported = false)
public interface FederationRepository extends CrudRepository<FederationDAO, String> {

    Optional<FederationDAO> findByCode(String code); // Use 'code' instead of 'dataModel'

    void deleteByCode(String code); // Use 'code' instead of 'dataModel'

    boolean existsByCode(String code); // Use 'code' instead of 'dataModel'
}
