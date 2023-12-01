CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE accounts
(
    name TEXT PRIMARY KEY,
    auth_token UUID NOT NULL UNIQUE,
    actual_size BIGINT NOT NULL CHECK (actual_size >= 0),
    total_size BIGINT NOT NULL CHECK (total_size >= 0),
    is_active BOOLEAN NOT NULL,
    tags JSONB NOT NULL
);
