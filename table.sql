DROP TABLE Grades;
DROP TABLE Validations;
DROP TABLE StudentCurriculums;
DROP TABLE CurriculumCourses;
DROP TABLE Courses;
DROP TABLE Curriculums;
DROP TABLE Teachers;
DROP TABLE Transfers;
DROP TABLE Deposits ;
DROP TABLE Students;



CREATE TABLE Students( 
    id SERIAL PRIMARY KEY, 
    last_name TEXT NOT NULL, 
    first_name TEXT NOT NULL, 
    phone_number TEXT NOT NULL,
    account DECIMAL NOT NULL CHECK (account >= 0 AND account < 1000000000) 
);

CREATE TABLE Deposits (
    id SERIAL PRIMARY KEY,
    id_student INTEGER NOT NULL REFERENCES Students(id) ON DELETE CASCADE,
    amount DECIMAL NOT NULL CHECK (amount >= 0),
    time_of_deposit TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE Transfers (
    id SERIAL PRIMARY KEY,
    id_issuer INTEGER NOT NULL REFERENCES Students(id) ON DELETE CASCADE,
    id_recipient INTEGER NOT NULL REFERENCES Students(id) ON DELETE CASCADE,
    amount DECIMAL NOT NULL CHECK (amount >= 0),
    time_of_transfer TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE Teachers( 
    id SERIAL PRIMARY KEY, 
    last_name TEXT NOT NULL, 
    first_name TEXT NOT NULL, 
    phone_number TEXT NOT NULL
);

CREATE TABLE Curriculums (
    id SERIAL PRIMARY KEY,
    curriculum_name TEXT NOT NULL,
    id_director INTEGER NOT NULL REFERENCES Teachers(id) ON DELETE CASCADE
);

CREATE TABLE Courses (
    id SERIAL PRIMARY KEY,
    course_name TEXT NOT NULL,
    id_teacher INTEGER NOT NULL REFERENCES Teachers(id) ON DELETE CASCADE
);

CREATE TABLE CurriculumCourses (
    id_curriculum INTEGER NOT NULL REFERENCES Curriculums(id) ON DELETE CASCADE,
    id_course INTEGER NOT NULL REFERENCES Courses(id) ON DELETE CASCADE,
    ects_credit INTEGER NOT NULL CHECK (ects_credit >= 0)
);

CREATE TABLE StudentCurriculums (
    id_student INTEGER NOT NULL REFERENCES Students(id) ON DELETE CASCADE,
    id_curriculum INTEGER NOT NULL REFERENCES Curriculums(id) ON DELETE CASCADE,
    UNIQUE(id_student, id_curriculum)
);

CREATE TABLE Validations (
    id SERIAL PRIMARY KEY,
    id_course INTEGER NOT NULL REFERENCES Courses(id) ON DELETE CASCADE,
    validation_name TEXT NOT NULL,
    coefficient INTEGER NOT NULL CHECK (coefficient >= 0),
    date_of_validation TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE Grades (
    id_student INTEGER NOT NULL REFERENCES Students(id) ON DELETE CASCADE,
    id_validation INTEGER NOT NULL REFERENCES Validations(id) ON DELETE CASCADE,
    grade DECIMAL NOT NULL CHECK (grade >= 0 AND grade <= 1),
    UNIQUE(id_student, id_validation)
);
