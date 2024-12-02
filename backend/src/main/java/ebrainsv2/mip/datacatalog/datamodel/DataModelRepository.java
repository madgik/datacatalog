package ebrainsv2.mip.datacatalog.datamodel;

import org.springframework.data.repository.CrudRepository;
import org.springframework.data.rest.core.annotation.RestResource;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

@RestResource(exported = false)
public interface DataModelRepository extends CrudRepository<DataModelDAO, String> {
    void deleteByUuid(UUID uuid);
    DataModelDAO findByUuid(UUID dataModelUuid);
    Optional<DataModelDAO> findByCodeAndVersion(String code, String version);
    List<DataModelDAO> findByReleased(boolean released);
}
