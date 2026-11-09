package ro.uaic.feaa.erasmus.shared;

public record AcademicYear(int startYear) {
    public AcademicYear { if (startYear < 2000) throw new IllegalArgumentException("Invalid academic year"); }
}
