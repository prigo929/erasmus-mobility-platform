package ro.uaic.feaa.erasmus.shared;

public record ECTSCredits(int value) {
    public ECTSCredits { if (value < 0) throw new IllegalArgumentException("Negative credits"); }
    public boolean isMinimumMet() { return value >= 30; }
    public ECTSCredits plus(ECTSCredits other) { return new ECTSCredits(Math.addExact(value, other.value)); }
}
