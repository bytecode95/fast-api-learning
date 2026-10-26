-- Allow access to the public schema
GRANT USAGE, CREATE
ON SCHEMA public
TO fastapi_app;

-- Grant privileges on existing tables
GRANT ALL PRIVILEGES
ON ALL TABLES IN SCHEMA public
TO fastapi_app;

-- Grant privileges on existing sequences
GRANT ALL PRIVILEGES
ON ALL SEQUENCES IN SCHEMA public
TO fastapi_app;