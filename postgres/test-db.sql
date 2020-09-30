CREATE USER test_db_user;
CREATE DATABASE calendar_test_db;
GRANT ALL PRIVILEGES ON DATABASE calendar_test_db TO test_db_user;
ALTER USER test_db_user WITH PASSWORD 'test_db_pw';
