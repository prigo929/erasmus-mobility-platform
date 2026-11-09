package ro.uaic.feaa.erasmus.agreement.domain;

import java.util.Objects;
import java.util.UUID;
import ro.uaic.feaa.erasmus.shared.ECTSCredits;

public record CourseLineTableB(UUID lineId, String homeCourseCode, String equivalentCourseTitle, ECTSCredits credits) {
    public CourseLineTableB { Objects.requireNonNull(lineId); Objects.requireNonNull(credits); }
}
