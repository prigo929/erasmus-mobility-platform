create table if not exists platform_state (
    kind varchar(40) not null,
    id uuid not null,
    payload clob not null,
    version bigint not null,
    primary key (kind, id)
);
create index if not exists idx_platform_state_kind on platform_state(kind);
