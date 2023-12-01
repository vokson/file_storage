CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE files
(
    id UUID PRIMARY KEY,
    stored_id UUID NOT NULL,
    name TEXT NOT NULL,
    size BIGINT NOT NULL CHECK (size >= 0),
    tag TEXT NOT NULL,
    created TIMESTAMPTZ NOT NULL,
    has_stored BOOLEAN NOT NULL DEFAULT FALSE,
    stored TIMESTAMPTZ,
    has_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    deleted TIMESTAMPTZ,
    has_erased BOOLEAN NOT NULL DEFAULT FALSE,
    erased TIMESTAMPTZ,

    account_name TEXT REFERENCES accounts (name) ON DELETE RESTRICT
);
