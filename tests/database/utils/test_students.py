import pytest
from pyshould import it

from database.models import Student
from database.utils import students
from services.exceptions import StudentNotFound


class TestStudents:
    def test_get_system_id_of_existing_student(self):

        test_student_id = 549350532

        student_id = students.get_system_id_of_student(test_student_id)

        it(student_id).should.be_equal(1)

    def test_get_system_id_of_non_existing_student(self):

        test_student_id = 55774545

        with pytest.raises(StudentNotFound):
            students.get_system_id_of_student(test_student_id)

    def test_get_active_students(self):

        test_group_id = 1

        students.get_active_students(test_group_id)

    def test_get_active_students_in_empty_group(self):

        test_group_id = 2

        with pytest.raises(StudentNotFound):
            students.get_active_students(test_group_id)

    def test_get_unique_second_name_letters_in_a_group(self):

        test_user_id = 549350532

        snd_names = students.get_unique_second_name_letters_in_a_group(test_user_id)

        it(snd_names).should.be_equal(["f", "Г"])

    def test_get_list_of_students_by_letter(self):

        test_letter = "Г"
        test_user_id = 549350532
        test_student = Student.get(id=1)

        st = students.get_list_of_students_by_letter(test_letter, test_user_id)

        it(st).should.be_equal([test_student])
