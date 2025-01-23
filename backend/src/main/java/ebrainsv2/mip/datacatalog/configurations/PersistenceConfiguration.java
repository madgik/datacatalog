package ebrainsv2.mip.datacatalog.configurations;

import org.flywaydb.core.Flyway;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.boot.jdbc.DataSourceBuilder;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.DependsOn;
import org.springframework.context.annotation.Primary;
import org.springframework.data.jpa.repository.config.EnableJpaRepositories;
import org.springframework.orm.jpa.JpaVendorAdapter;
import org.springframework.orm.jpa.LocalContainerEntityManagerFactoryBean;
import org.springframework.orm.jpa.vendor.HibernateJpaVendorAdapter;

import javax.sql.DataSource;


@Configuration
@EnableJpaRepositories({"ebrainsv2.mip.datacatalog.datamodel", "ebrainsv2.mip.datacatalog.federation"})
public class PersistenceConfiguration {

    @Primary
    @Bean(name = "datasource")
    @ConfigurationProperties(prefix = "spring.datasource")
    public DataSource datacatalogDataSource() {
        DataSourceBuilder<?> builder = DataSourceBuilder.create();
        builder.url("jdbc:postgresql://datacatalogdb:5432/postgres");
        builder.username("postgres");
        builder.password("test");
        builder.driverClassName("org.postgresql.Driver");
        return builder.build();
    }

    @Bean(name = "entityManagerFactory")
    @DependsOn("flyway")
    public LocalContainerEntityManagerFactoryBean entityManagerFactory() {
        LocalContainerEntityManagerFactoryBean emfb = new LocalContainerEntityManagerFactoryBean();
        emfb.setDataSource(datacatalogDataSource());
        JpaVendorAdapter vendorAdapter = new HibernateJpaVendorAdapter();
        emfb.setJpaVendorAdapter(vendorAdapter);
        emfb.setPackagesToScan("ebrainsv2.mip.datacatalog");
        return emfb;
    }

    @Bean(name = "flyway", initMethod = "migrate")
    public Flyway migrations() {
        return Flyway.configure()
                .dataSource(datacatalogDataSource())
                .baselineOnMigrate(true)
                .load();

    }
}
