CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(255) NOT NULL
);
-- Insert a student
INSERT INTO users (username, password, role) VALUES ('student1', 'student_password', 'student');

-- Insert a teacher
INSERT INTO users (username, password, role) VALUES ('teacher1', 'teacher_password', 'teacher');
