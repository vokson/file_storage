CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE accounts
(
    id UUID PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    auth_token UUID NOT NULL UNIQUE,
    is_active BOOLEAN NOT NULL
);
