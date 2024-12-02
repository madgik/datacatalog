package ebrainsv2.mip.datacatalog.datamodel;

public class InvalidDataModelError extends RuntimeException {
    public InvalidDataModelError(String message) {
        super(message);
    }
}