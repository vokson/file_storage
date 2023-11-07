CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE files
(
    id UUID PRIMARY KEY,
    stored_id UUID NOT NULL,
    name TEXT NOT NULL,
    size BIGINT NOT NULL CHECK (size >= 0),
    created TIMESTAMP NOT NULL,
    has_stored BOOLEAN DEFAULT FALSE,
    stored TIMESTAMP,
    has_deleted BOOLEAN DEFAULT FALSE,
    deleted TIMESTAMP,
    has_erased BOOLEAN DEFAULT FALSE,
    erased TIMESTAMP,

    account_id UUID REFERENCES accounts (id) ON DELETE RESTRICT
);
