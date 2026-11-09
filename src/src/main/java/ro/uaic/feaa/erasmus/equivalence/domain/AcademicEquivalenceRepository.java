package ro.uaic.feaa.erasmus.equivalence.domain;

import java.util.Optional;
import ro.uaic.feaa.erasmus.shared.EquivalenceId;

public interface AcademicEquivalenceRepository {
    Optional<AcademicEquivalence> findByCourseCodes(String sendCode, String hostCode);
    Optional<AcademicEquivalence> findById(EquivalenceId id);
    void save(AcademicEquivalence equivalence);
}
