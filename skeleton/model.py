#!/usr/bin/python

import sys
import psycopg2
import psycopg2.extras
import time


class Model:
    def __init__(self):
        self.connection = psycopg2.connect("dbname='webdb' user='dihellgo' host='127.0.0.1'")
        self.connection.autocommit = True
        self.cursor = self.connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        if (self.connection):
            self.connection.close()

##############################################
######     Queries for tab STUDENTS     ######
##############################################

    # TODO 01 - Easy
    # Create a new student and associated account.
    def createStudent(self, lastname, firstname, phone):
        self.cursor.execute(f"""
        INSERT INTO Students( last_name, first_name, phone_number, account) VALUES ('{lastname}', '{firstname}', '{phone}', 0)
        """)

    # TODO 02 - Easy
    # Return a list of (id, lastname, firstname, phone,
    # number of curriculums) corresponding to all students,
    # ordered by their last names.
    def listStudents(self):
        self.cursor.execute(f"""
        SELECT id, last_name, first_name, phone_number, COUNT(id_student) FROM Students
                            LEFT JOIN StudentCurriculums ON id_student = id
                            GROUP BY id
                            ORDER BY last_name
        """)
        return self.cursor.fetchall()

    # TODO 03 - Easy
    # Delete a student given its ID (beware of the foreign constraints!).
    def deleteStudent(self, idStudent):
        # DELETE FROM Deposits WHERE id_student = {idStudent};
        # DELETE FROM Transfers WHERE id_issuer = {idStudent};
        # DELETE FROM Transfers WHERE id_recipient = {idStudent};
        # DELETE FROM StudentCurriculums WHERE id_student = {idStudent};
        # DELETE FROM Grades WHERE id_student = {idStudent};
        self.cursor.execute(f"""
        DELETE FROM Students WHERE id = {idStudent}
        """)

##############################################
######     Queries for tab ACCOUNTS     ######
##############################################

    # TODO 04 - Easy
    # Return a list of (id, full name, account balance)
    # corresponding to all student accounts.
    def listAccounts(self):
        self.cursor.execute(f"""
        SELECT id, first_name || ' ' || last_name, account FROM Students 
        ORDER BY last_name
        """)
        return self.cursor.fetchall()

    # TODO 05 - Medium
    # Update the database to take into account a deposit.
    def deposit(self, account, amount):
        self.cursor.execute(f"""
        UPDATE Students SET account = account + {amount} WHERE id = {account} 
        """)
        self.cursor.execute(f"""
        INSERT INTO Deposits (id_student, amount) VALUES ({account}, {amount})
        """)


    # TODO 06 - Medium
    # Return the amount of money transfered by a given student
    # over the last 24 hours, plus some given additional amount.
    # Do not forget to handle the case where there is no transfers
    # in the last 24 hours.
    def getTransferedAmountOver24Hours(self, id, additional):
        self.cursor.execute(f"""
        SELECT SUM(amount) FROM Transfers WHERE id_issuer = {id} AND time_of_transfer > NOW() - INTERVAL '24' HOUR GROUP BY id_issuer
        """)
        res = self.cursor.fetchall()
        assert len(res) <= 1
        if res == []:
            return additional
        else :
            print(res[0][0])
            return res[0][0] + additional

    # TODO 07 - Medium
    # Updates the database to take into account a transfer from
    # a given issuer account to a given recipient account, ensuring that:
    # - The issuer account has enough money;
    # - After exercise 5: the total amount transfered from
    #   the issuer account over 24 hours is not greater than 1000€.
    def transfer(self, issuer, recipient, amount):
        if issuer == recipient :
            raise Exception("Cannot transfer money from an account to itself")
        self.cursor.execute(f"""
            BEGIN TRANSACTION;
            LOCK TABLE Transfers
        """)
        if self.getTransferedAmountOver24Hours(issuer, amount) > 1000 :
            raise Exception("Maximum amount of transfer over a 24h window reached (=1000€)")
        self.cursor.execute(f"""
        SELECT account FROM Students WHERE id = {issuer} """)
        if self.cursor.fetchall()[0][0] < amount :
            raise Exception("Issuer doesn't enough money to make this transfer")
        time.sleep(5)
        self.cursor.execute(f"""
            UPDATE Students SET account = account - {amount} WHERE id = {issuer}""")
        time.sleep(5)
        self.cursor.execute(f""" 
            UPDATE Students SET account = account + {amount} WHERE id = {recipient}
        """)
        self.cursor.execute(f""" 
            INSERT INTO Transfers(id_issuer, id_recipient, amount) VALUES ({issuer}, {recipient}, {amount});
            COMMIT""")
##############################################
######   Queries for tab ACCOUNTS/<ID>  ######
##############################################

    # TODO 08 - Medium
    # Return a list of (id, date, operation type, from/to, amount)
    # of all operations on the account of a given student, sorted by
    # decreasing date.
    # Operation type is either "Deposit", "Received transfer" or
    # "Sent transfer", and from/to is the full name of the other
    # person involved if the operation is a transfer, and a NULL
    # otherwise.
    def listTransOfStudent(self, id):
        self.cursor.execute(f"""
        (SELECT id, time_of_deposit, 'Deposit', NULL, amount FROM Deposits WHERE id_student = {id})
        UNION
        (SELECT Transfers.id, time_of_transfer, 'Sent transfer', first_name || ' ' || last_name, amount FROM Transfers  
        JOIN Students ON id_recipient = Students.id 
        WHERE id_issuer = {id})
        UNION
        (SELECT Transfers.id, time_of_transfer, 'Received transfer', first_name || ' ' || last_name, amount FROM Transfers  
        JOIN Students ON id_issuer = Students.id 
        WHERE id_recipient = {id})

        ORDER BY 2 DESC
        """)
        return self.cursor.fetchall()


##############################################
######     Queries for tab TEACHERS     ######
##############################################

    # TODO 09 - Easy
    # Create a new teacher.
    def createTeacher(self, lastname, firstname, phone):
        self.cursor.execute(f"""
        INSERT INTO Teachers (last_name, first_name, phone_number) VALUES ('{lastname}', '{firstname}', '{phone}')
        """)

    # TODO 10 - Easy
    # Return a list of (id, lastname, firstname, phone,
    # number of curriculums) corresponding to all teachers.
    def listTeachers(self):
        self.cursor.execute(f"""
        SELECT Teachers.id, last_name, first_name, phone_number, COUNT(Curriculums.id) FROM Teachers
                    LEFT JOIN Curriculums ON id_director = Teachers.id
                    GROUP BY Teachers.id
                    ORDER BY last_name
        """)
        return self.cursor.fetchall()

    # TODO 11 - Easy
    # Delete a teacher given its ID (beware of the foreign constraints!).
    def deleteTeacher(self, idTeacher):
        self.cursor.execute(f"""
        DELETE FROM Teachers WHERE id = {idTeacher}
        """)

##############################################
######     Queries for CURRICULUMS      ######
##############################################

    # TODO 12 - Easy
    # Create a curriculum.
    def createCurriculum(self, name, director):
        self.cursor.execute(f"""
        INSERT INTO Curriculums ( curriculum_name, id_director ) VALUES ('{name}', '{director}')
        """)

    # TODO 13 - Easy
    # Return a list of (id,name of curriculum,director lastname,
    # director firstname) corresponding to all curriculums.
    def listCurriculums(self):
        self.cursor.execute(f"""
        SELECT Curriculums.id, curriculum_name, last_name,  first_name
                            FROM Curriculums
                            JOIN Teachers ON id_director = Teachers.id
        """)
        return self.cursor.fetchall()

    # TODO 14 - Easy
    # Delete a curriculum given its ID (beware of the foreign constraints!).
    def deleteCurriculum(self, idCurriculum):
        self.cursor.execute(f"""
        DELETE FROM Curriculums WHERE id = {idCurriculum}
        """)

##############################################
######     Queries for  COURSES         ######
##############################################

    # TODO 15 - Easy
    # Create a course.
    def createCourse(self, name, idProfessor):
        self.cursor.execute(f"""
        INSERT INTO Courses (course_name, id_teacher) 
        VALUES ('{name}', {idProfessor})
        """)

    # TODO 16 - Easy
    # Return a list of (course id, course name, teacher id,
    # teacher last name, teacher first name) corresponding
    # to all the courses.
    def listCourses(self):
        self.cursor.execute(f"""
        SELECT Courses.id, course_name, id_teacher, last_name, first_name
        FROM Courses JOIN Teachers
        ON Teachers.id = id_teacher
        """)
        return self.cursor.fetchall()

    # TODO 14 - Easy
    # Delete a given course (beware that the course might be registered to
    # curriculum, and have grades that should also be deleted).
    def deleteCourse(self, idCourse):
        # TODO : Check if other things should be deleted
        self.cursor.execute(f"""
        DELETE FROM Courses WHERE id = {idCourse}
        """)


##############################################
###### Queries for tab  CURRICULUM/<ID> ######
##############################################

    # TODO 18 - Easy
    # Get the name of a given curriculum.
    def getNameOfCurriculum(self, id):
        self.cursor.execute(f"""
        SELECT curriculum_name FROM Curriculums WHERE id = {id}
        """)
        # suppose that there is a solution
        return self.cursor.fetchall()[0][0]

    # TODO 19 - Easy
    # Return the list (course id, course name, teacher full name, ECTS)
    # corresponding to the courses, registered to a given curriculum.
    def listCoursesOfCurriculum(self, idCurriculum):
        self.cursor.execute(f"""
        SELECT Courses.id, Courses.name, Teachers.first_name || ' ' || Teachers.last_name, ects_credit
        FROM Curriculumcourses
        JOIN Courses, Teachers
        ON Courses.id = id_course, Teachers.id = id_teacher
        WHERE id_curriculum = {idCurriculum}
        """)
        return self.cursor.fetchall()

    # TODO 20 - Hard
    # Return a list (full name, average grade) of students
    # registered to a given curriculum. The
    # average grade is computed as described in the document, but
    # beware that if a student does not have a grade for a validation
    # or is not registered to a course, he should have 0.
    def averageGradesOfStudentsInCurriculum(self, idCurriculum):
        self.cursor.execute(f"""
        SELECT Students.first_name || ' ' Students.last_name, SUM(COALESCE(grade, 0))/SUM(coefficient)
        FROM StudentCurriculum as sc
        JOIN Students, Curriculumcourses as cc, Validations
        ON Students.id = sc.id_student, cc.id_curriculum = sc.id_curriculum, Validations.id_course = cc.id_course
        LEFT JOIN Grades as g
        ON g.id_validation = Validations.id, g.id_student = Students.id
        WHERE id_curriculum = {idCurriculum}
        GROUP BY Students.id
        """)
        return self.cursor.fetchall()

    # TODO 21 - Easy
    # Register a student to a curriculum.
    def registerStudentToCurriculum(self, idStudent, idCurriculum):
        self.cursor.execute(f"""
        INSERT INTO StudentCurriculums (id_student, id_curriculum) VALUES ({idStudent}, {idCurriculum})
        """)

    # TODO 22 - Easy
    # Register a course to a curriculum.
    def registerCourseToCurriculum(self, idCourse, idCurriculum, ects):
        self.cursor.execute(f"""
        TODO
        """)

    # TODO 23 - Easy
    # Unregister a course to a curriculum.
    def deleteCourseFromCurriculum(self, idCourse, idCurriculum):
        self.cursor.execute(f"""
        TODO
        """)

##############################################
######   Queries for tab  COURSE/<ID>   ######
##############################################

    # TODO 24 - Easy
    # Get the name of a given course.
    def getNameOfCourse(self, id):
        self.cursor.execute(f"""
        TODO
        """)
        # suppose that there is a solution
        return self.cursor.fetchall()[0][0]

    # TODO 25 - Easy
    # Return a list of (id, name, ECTS) of the curriculums in
    # which a given course is registered.
    def listCurriculumsOfCourse(self, idCourse):
        self.cursor.execute(f"""
        TODO
        """)
        return self.cursor.fetchall()

    # TODO 26 - Easy
    # Returns a list of (id, date, name, coefficent) for the validations
    # assiociated to a given course.
    def listValidationsOfCourse(self, idCourse):
        self.cursor.execute(f"""
        TODO
        """)
        return self.cursor.fetchall()

    # TODO 27 - Hard
    # Return a list (id, full name, average grade) of students that are
    # registered in a curriculum with the given course. The
    # average grade is computed as described in the document, but
    # beware that if a student does not have a grade for a validation
    # or is not registered to a course, he should have 0.
    def listStudentsOfCourse(self, idCourse):
        self.cursor.execute(f"""
        TODO
        """)
        return self.cursor.fetchall()

    # TODO 28 - Medium
    # Return a list (id, date, curriculum name, student full name,
    # validation name, grade, coefficient) of grades for all the
    # validations and students having taken them, sorted by decreasing
    # date of validation.
    def listGradesOfCourse(self, idCourse):
        self.cursor.execute(f"""
        TODO
        """)
        return self.cursor.fetchall()

    # TODO 29 - Easy
    # Add a validation to a given course.
    def addValidationToCourse(self, name, coef, date, idCourse):
        self.cursor.execute(f"""
        TODO
        """)

    # TODO 30 - Easy
    # Add a grade to a student.
    def addGrade(self, idValidation, idStudent, grade):
        self.cursor.execute(f"""
        TODO
        """)

##############################################
######       Queries for tab            ######
######      COURSE/<ID1>/<ID2           ######
###### corresponding to validations     ######
##############################################

    # TODO 31 - Easy
    # Return a list (full name, grade) of grades for
    # a given validation.
    def listGradesOfValidation(self, idValidation):
        self.cursor.execute(f"""
        TODO
        """)
        return self.cursor.fetchall()

    # TODO 32 - Easy
    # Get the complete name of a validation given its ID. The
    # complete name of a validation with name "exam" of a course "BDD"
    # is "BDD - exam". You should therefore preppend the name of the
    # course.
    def getNameOfValidation(self, id):
        self.cursor.execute(f"""
        TODO
        """)
        # suppose that there is a solution
        return self.cursor.fetchall()[0][0]

##############################################
######   Queries for tab  TEACHER/<ID>  ######
##############################################

    # TODO 33 - Easy
    # Get the name of a teacher given its ID.
    def getNameOfTeacher(self, id):
        self.cursor.execute(f"""
        TODO
        """)
        # suppose that there is a solution
        return self.cursor.fetchall()[0][0]

    # TODO 34 - Easy
    # Return a list (name) of all the curriculums supervised
    # by a given teacher
    def listCurriculumsOfTeacher(self, idTeacher):
        self.cursor.execute(f"""
        TODO
        """)
        return self.cursor.fetchall()

    # TODO 35 - Easy
    # Return a list (name) of all the courses supervised
    # by a given teacher
    def listCoursesOfTeacher(self, idTeacher):
        self.cursor.execute(f"""
        TODO
        """)
        return self.cursor.fetchall()

    # TODO 36 - Medium
    # Return a list (date, course name, exam name) of exams
    # for all courses taught by a given teacher, such that the
    # due date is passed and there is no grade for at least one
    # registered studentgrades for a given student, sorted
    # by increasing date of validation.
    def listValidationsOfTeacherToGrade(self, idTeacher):
        self.cursor.execute(f"""
        TODO
        """)
        return self.cursor.fetchall()


##############################################
######   Queries for tab  STUDENT/<ID>  ######
##############################################

    # TODO 37 - Easy
    # Get the name of a student given its ID.
    def getNameOfStudent(self, id):
        self.cursor.execute(f"""
        SELECT first_name || ' ' || last_name FROM Students WHERE id = {id}
        """)
        # suppose that there is a solution
        return self.cursor.fetchall()[0][0]

    # TODO 38 - Medium
    # Return a list (id, date, curriculum name, course name,
    # exam name, grade) of grades for a given student, sorted
    # by decreasing date of validation.
    def listValidationsOfStudent(self, idStudent):
        self.cursor.execute(f"""
        TODO
        """)
        return self.cursor.fetchall()

    # TODO 39 - Hard
    # Return a list (curriculum name, average grade) of all the
    # curriculum a given student is registered to, where the
    # average grade is computed as before.
    def listCurriculumsOfStudent(self, idStudent):
        self.cursor.execute(f"""
        TODO
        """)
        return self.cursor.fetchall()
