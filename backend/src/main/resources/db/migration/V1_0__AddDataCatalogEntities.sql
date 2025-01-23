CREATE TABLE data_model (
                            uuid UUID PRIMARY KEY,
                            code VARCHAR(255) NOT NULL,
                            version VARCHAR(255) NOT NULL,
                            label VARCHAR(255) NOT NULL,
                            longitudinal BOOLEAN NOT NULL,
                            variables TEXT,
                            groups TEXT,
                            released BOOLEAN
);

CREATE TABLE federation (
                            code VARCHAR(255) PRIMARY KEY,
                            title VARCHAR(255),
                            url VARCHAR(255),
                            records INT,
                            institutions INT,
                            description VARCHAR(3000)
);

CREATE TABLE federation_data_model (
                                       federation_code VARCHAR(255),
                                       data_model_uuid UUID,
                                       PRIMARY KEY (federation_code, data_model_uuid),
                                       FOREIGN KEY (federation_code) REFERENCES federation(code) ON DELETE CASCADE,
                                       FOREIGN KEY (data_model_uuid) REFERENCES data_model(uuid) ON DELETE CASCADE
);
