package ro.uaic.feaa.erasmus.agreement.domain;

import java.util.Optional;
import ro.uaic.feaa.erasmus.shared.AgreementId;

public interface LearningAgreementRepository {
    Optional<LearningAgreement> findById(AgreementId id);
    void save(LearningAgreement agreement);
}
