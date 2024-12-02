package ebrainsv2.mip.datacatalog.federation;

import ebrainsv2.mip.datacatalog.datamodel.DataModelDAO;
import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

@Entity
@Data
@NoArgsConstructor
@AllArgsConstructor
@Table(name = "federation")
public class FederationDAO {

    @Id
    @Column(nullable = false, unique = true)
    private String code;

    private String title;
    private String url;
    private int records;
    private int institutions;
    private String description;

    @ManyToMany
    @JoinTable(
            name = "federation_data_model",
            joinColumns = @JoinColumn(name = "federation_code"),
            inverseJoinColumns = @JoinColumn(name = "data_model_uuid")
    )
    private List<DataModelDAO> dataModels;
}
