package ro.uaic.feaa.erasmus.preparation.domain;

import java.util.Optional;
import ro.uaic.feaa.erasmus.shared.*;

public interface MobilityChecklistRepository {
    void save(MobilityChecklist checklist);
    Optional<MobilityChecklist> findByAgreementId(AgreementId agreementId);
    Optional<MobilityChecklist> findByStudentId(StudentId studentId);
}
