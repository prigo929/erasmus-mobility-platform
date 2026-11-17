package ro.uaic.feaa.erasmus.platform;

import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

@Component
public class OutboxWorker {
    private final PlatformService platform;
    public OutboxWorker(PlatformService platform) { this.platform = platform; }
    @Scheduled(fixedDelayString = "${platform.outbox.poll-ms:1000}")
    public void deliverPendingEvents() {
        platform.processOutbox();
        platform.flagOverdueTasks(java.time.LocalDate.now());
    }
}
