package ro.uaic.feaa.erasmus.equivalence.domain;

import java.util.Objects;
import java.util.UUID;
import ro.uaic.feaa.erasmus.shared.*;

public record CourseSyllabus(CourseCode code, String courseName, ECTSCredits credits, UUID universityId) {
    public CourseSyllabus { Objects.requireNonNull(code); Objects.requireNonNull(credits); Objects.requireNonNull(universityId); }
}
