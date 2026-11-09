package ro.uaic.feaa.erasmus.agreement.domain;

public interface IEquivalenceCatalogAdapter {
    EquivalenceVerificationResult checkEquivalence(String sendCode, String hostCode);
}
