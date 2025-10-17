CREATE DATABASE IF NOT EXISTS nyc311;
USE nyc311;

CREATE TABLE IF NOT EXISTS service_requests (
  unique_key BIGINT PRIMARY KEY,
  created_date DATETIME NOT NULL,
  closed_date DATETIME NULL,
  agency VARCHAR(16),
  complaint_type VARCHAR(128),
  descriptor VARCHAR(255),
  borough VARCHAR(32),
  latitude DECIMAL(9,6),
  longitude DECIMAL(9,6)
);

-- Add indexes for performance optimization
CREATE INDEX idx_borough ON service_requests (borough);
CREATE INDEX idx_created_date ON service_requests (created_date);
CREATE INDEX idx_complaint_type ON service_requests (complaint_type);
