package ebrainsv2.mip.datacatalog.datamodel;

import com.google.gson.annotations.Expose;
import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.UUID;

@Entity
@Data
@NoArgsConstructor
@AllArgsConstructor
@Table(name = "`data_model`")
public class DataModelDAO {

    @Expose
    @Id
    @GeneratedValue
    @Column(columnDefinition = "uuid", updatable = false)
    private UUID uuid;

    @Expose
    private String code;

    @Expose
    private String version;

    @Expose
    private String label;

    @Expose
    private Boolean longitudinal;

    @Expose
    private String variables;

    @Expose
    private String groups;

    @Expose
    private Boolean released;
}
