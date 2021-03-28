import pytest
from pony import orm
from pyexpect import expect

from jacob.database.models import Student, Group
from jacob.database.utils import admin, students
from jacob.services.exceptions import StudentNotFound


class TestStudents:
    def test_get_system_id_of_existing_student(self):

        test_student_id = 549350532

        student_id = students.get_system_id_of_student(test_student_id)

        expect(student_id).is_equal(23)

    def test_get_system_id_of_non_existing_student(self):

        test_student_id = 55774545

        with pytest.raises(StudentNotFound):
            students.get_system_id_of_student(test_student_id)

    @orm.db_session
    def test_get_active_students(self):

        test_group_id = 6

        students_ = students.get_active_students(Group[test_group_id])

        expect(students_).not_is_empty()

    @orm.db_session
    def test_get_active_students_in_empty_group(self):

        test_group_id = 9

        with pytest.raises(StudentNotFound):
            students.get_active_students(Group[test_group_id])

    @orm.db_session
    def test_get_unique_second_name_letters_in_a_group(self):

        test_user_id = 23

        snd_names = students.get_unique_second_name_letters_in_a_group(
            admin.get_active_group(test_user_id),
        )

        expect(snd_names).is_equal(sorted(list("БДСМЛЯВКИГЖРТЗШ")))

    @orm.db_session
    def test_get_list_of_students_by_letter(self):

        test_letter = "С"
        test_user_id = 23

        with orm.db_session:
            test_student = Student[41]

        st = students.get_list_of_students_by_letter(test_user_id, test_letter)[:]

        expect(st).is_equal([test_student])
