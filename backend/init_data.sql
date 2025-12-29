

--  DB 생성 (별도 실행 필요: psql -U postgres)
CREATE DATABASE shopping;

--  테이블 삭제 (순서 중요: FK 있는 테이블 먼저)
DROP TABLE IF EXISTS user_sessions;
DROP TABLE IF EXISTS users;

SELECT * FROM users;
SELECT * FROM user_sessions;

--  users 테이블 생성
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(30) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_dt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- user_sessions 테이블 생성
CREATE TABLE user_sessions (
    id VARCHAR(36) NOT NULL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    revoked_at TIMESTAMP NULL,

    CONSTRAINT fk_user_sessions_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);

-- 인덱스 생성
CREATE INDEX ix_users_username ON users(username);
CREATE INDEX ix_users_email ON users(email);
CREATE INDEX ix_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX ix_user_sessions_valid ON user_sessions(user_id, expires_at, revoked_at);

SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';
