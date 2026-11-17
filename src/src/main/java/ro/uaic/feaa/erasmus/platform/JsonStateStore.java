package ro.uaic.feaa.erasmus.platform;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Repository;

@Repository
public class JsonStateStore {
    private final JdbcTemplate jdbc;
    private final ObjectMapper json;

    public JsonStateStore(JdbcTemplate jdbc, ObjectMapper json) {
        this.jdbc = jdbc;
        this.json = json;
    }

    public <T> Optional<T> find(String kind, UUID id, Class<T> type) {
        return jdbc.query("select payload from platform_state where kind=? and id=?",
            rs -> rs.next() ? Optional.of(read(rs.getString(1), type)) : Optional.empty(), kind, id);
    }

    public <T> List<T> findAll(String kind, Class<T> type) {
        return jdbc.query("select payload from platform_state where kind=? order by id",
            (rs, row) -> read(rs.getString(1), type), kind);
    }

    public void insert(String kind, UUID id, Object value, long version) {
        jdbc.update("insert into platform_state(kind,id,payload,version) values (?,?,?,?)",
            kind, id, write(value), version);
    }

    public void update(String kind, UUID id, long expectedVersion, Object value, long newVersion) {
        int changed = jdbc.update("update platform_state set payload=?,version=? where kind=? and id=? and version=?",
            write(value), newVersion, kind, id, expectedVersion);
        if (changed != 1) throw new IllegalStateException("Versiune modificată de altă solicitare; reîncarcă datele.");
    }

    public boolean exists(String kind, UUID id) {
        Integer count = jdbc.queryForObject("select count(*) from platform_state where kind=? and id=?", Integer.class, kind, id);
        return count != null && count > 0;
    }

    private String write(Object value) {
        try { return json.writeValueAsString(value); }
        catch (JsonProcessingException error) { throw new IllegalStateException("Starea nu poate fi serializată.", error); }
    }

    private <T> T read(String value, Class<T> type) {
        try { return json.readValue(value, type); }
        catch (JsonProcessingException error) { throw new IllegalStateException("Starea salvată nu poate fi citită.", error); }
    }
}
