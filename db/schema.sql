CREATE TABLE IF NOT EXISTS service_requests (
    request_id BIGINT PRIMARY KEY,
    created_datetime DATETIME NOT NULL,
    closed_datetime DATETIME NULL,
    agency VARCHAR(16),
    agency_name VARCHAR(128),
    complaint_type VARCHAR(128),
    descriptor VARCHAR(255),
    borough VARCHAR(32),
    city VARCHAR(64),
    latitude DECIMAL(9,6),
    longitude DECIMAL(9,6),
    status VARCHAR(32),
    resolution_description TEXT,
    month_key VARCHAR(7)
);