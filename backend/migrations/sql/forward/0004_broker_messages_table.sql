CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE broker_messages
(
    id UUID PRIMARY KEY,
    direction VARCHAR(1) NOT NULL CHECK (direction = ANY(ARRAY['O', 'I'])),
    app TEXT NOT NULL,
	"key" TEXT NOT NULL,
	body jsonb NOT NULL,
	has_executed BOOLEAN NOT NULL,
	created timestamptz NOT NULL,
	updated timestamptz NOT NULL,
	has_execution_stopped BOOLEAN NOT NULL,
	count_of_retries INTEGER NOT NULL,
	next_retry_at timestamptz NOT NULL,
	seconds_to_next_retry INTEGER NOT NULL,
	CONSTRAINT count_of_retries_not_negative CHECK (count_of_retries >= 0),
	CONSTRAINT seconds_to_next_retry_not_negative CHECK (seconds_to_next_retry > 0)
);

CREATE INDEX broker_messages_has_executed ON broker_messages ((1)) WHERE has_executed = FALSE;
CREATE INDEX broker_messages_has_execution_stopped ON broker_messages ((1)) WHERE has_execution_stopped = FALSE;
