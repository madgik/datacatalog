package ebrainsv2.mip.datacatalog.datamodel;

import java.util.List;

public class DataModelValidator {

    public static boolean containsRequiredDataset(List<CommonDataElementDTO> variables, List<DataModelMetadataGroupDTO> groups) {
        boolean datasetValid = false;

        if (variables != null) {
            datasetValid = variables.stream()
                    .anyMatch(v -> v.code().equals("dataset") &&
                            v.sql_type().equals("text") &&
                            Boolean.TRUE.equals(v.isCategorical()));
        }

        if (!datasetValid && groups != null) {
            datasetValid = groups.stream()
                    .anyMatch(g -> containsRequiredDataset(g.variables(), g.groups()));
        }

        return datasetValid;
    }


    public static void validateLongitudinalElements(List<CommonDataElementDTO> variables, List<DataModelMetadataGroupDTO> groups) {
        validateSubjectId(variables, groups); // Validate presence of subjectid
        validateVisitId(variables, groups); // Validate visitid with specific criteria
    }

    private static void validateSubjectId(List<CommonDataElementDTO> variables, List<DataModelMetadataGroupDTO> groups) {
        boolean hasSubjectId = variables.stream().anyMatch(v -> v.code().equals("subjectid")) ||
                groups.stream().anyMatch(g -> validatePresenceInGroup(g, "subjectid"));

        if (!hasSubjectId) {
            throw new InvalidDataModelError("CDE 'subjectid' is missing for a longitudinal study.");
        }
    }

    private static void validateVisitId(List<CommonDataElementDTO> variables, List<DataModelMetadataGroupDTO> groups) {
        boolean hasValidVisitId = variables.stream().anyMatch(DataModelValidator::isValidVisitId) ||
                groups.stream().anyMatch(DataModelValidator::validateValidVisitIdInGroup);

        if (!hasValidVisitId) {
            throw new InvalidDataModelError("CDE 'visitid' does not meet the required conditions for a longitudinal study.");
        }
    }

    static boolean isValidVisitId(CommonDataElementDTO v) {
        return "visitid".equals(v.code()) && Boolean.TRUE.equals(v.isCategorical()) && "text".equals(v.sql_type()) && v.enumerations() != null;
    }

    private static boolean validatePresenceInGroup(DataModelMetadataGroupDTO group, String code) {
        boolean foundInVariables = group.variables() != null &&
                group.variables().stream().anyMatch(v -> code.equals(v.code()));

        boolean foundInGroups = !foundInVariables && group.groups() != null &&
                group.groups().stream().anyMatch(g -> validatePresenceInGroup(g, code));

        return foundInVariables || foundInGroups;
    }

    private static boolean validateValidVisitIdInGroup(DataModelMetadataGroupDTO group) {
        boolean validVisitIdFound = group.variables() != null &&
                group.variables().stream().anyMatch(DataModelValidator::isValidVisitId);

        boolean validVisitIdInGroups = !validVisitIdFound && group.groups() != null &&
                group.groups().stream().anyMatch(DataModelValidator::validateValidVisitIdInGroup);

        return validVisitIdFound || validVisitIdInGroups;
    }
}
