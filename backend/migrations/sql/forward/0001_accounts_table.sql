CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE accounts
(
    name TEXT PRIMARY KEY,
    auth_token UUID NOT NULL UNIQUE,
    is_active BOOLEAN NOT NULL
);
