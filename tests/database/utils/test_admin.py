import pytest
from pyshould import it

from database.utils import admin
from services.exceptions import UserIsNotAnAdministrator


class TestAdmin:
    def test_is_user_admin(self):

        test_student_id = 1

        status = admin.is_user_admin(test_student_id)

        it(status).should.be_equal(True)

    def test_is_non_admin_is_admin(self):
        from database.utils.admin import is_user_admin

        test_student_id = 2

        with pytest.raises(UserIsNotAnAdministrator):
            is_user_admin(test_student_id)

    def test_get_admin_storage(self):

        test_student_id = 1

        try:
            admin.get_admin_storage(test_student_id)
        except UserIsNotAnAdministrator:
            pytest.fail()

    def test_get_non_admin_storage(self):

        test_student_id = 2

        with pytest.raises(UserIsNotAnAdministrator):
            admin.get_admin_storage(test_student_id)
