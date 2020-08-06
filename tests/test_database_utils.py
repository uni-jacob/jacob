import pytest
from pyshould import it

from utils.exceptions import UserIsNotAnAdministrator


class TestDatabaseUtils:
    def test_get_system_id_of_existing_student(self):
        from database.utils import get_system_id_of_student

        test_student_id = 549350532

        student_id = get_system_id_of_student(test_student_id)

        it(student_id).should.be_equal(1)

    def test_get_system_id_of_non_existing_student(self):
        from database.utils import get_system_id_of_student
        from utils.exceptions import StudentNotFound

        test_student_id = 55774545

        with pytest.raises(StudentNotFound):
            get_system_id_of_student(test_student_id)

    def test_is_user_admin(self):
        from database.utils import is_user_admin

        test_student_id = 1

        status = is_user_admin(test_student_id)

        it(status).should.be_equal(True)

    def test_is_non_admin_is_admin(self):
        from database.utils import is_user_admin

        test_student_id = 2

        with pytest.raises(UserIsNotAnAdministrator):
            is_user_admin(test_student_id)

    def test_get_admin_storage(self):
        from database.utils import get_admin_storage

        test_student_id = 1

        try:
            get_admin_storage(test_student_id)
        except UserIsNotAnAdministrator:
            pytest.fail()

    def test_get_non_admin_storage(self):
        from database.utils import get_admin_storage

        test_student_id = 2

        with pytest.raises(UserIsNotAnAdministrator):
            get_admin_storage(test_student_id)

    def test_get_active_students(self):
        from database.utils import get_active_students

        test_group_id = 1

        get_active_students(test_group_id)
