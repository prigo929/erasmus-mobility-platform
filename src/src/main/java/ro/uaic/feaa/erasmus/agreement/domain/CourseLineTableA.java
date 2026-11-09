package ro.uaic.feaa.erasmus.agreement.domain;

import java.util.Objects;
import java.util.UUID;
import ro.uaic.feaa.erasmus.shared.ECTSCredits;

public record CourseLineTableA(UUID lineId, String hostCourseCode, String courseTitle, ECTSCredits credits) {
    public CourseLineTableA { Objects.requireNonNull(lineId); Objects.requireNonNull(credits); }
}
