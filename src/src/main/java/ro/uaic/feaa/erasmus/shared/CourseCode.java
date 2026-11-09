package ro.uaic.feaa.erasmus.shared;

public record CourseCode(String value) {
    public CourseCode { if (value == null || value.isBlank()) throw new IllegalArgumentException("Empty course code"); }
}
