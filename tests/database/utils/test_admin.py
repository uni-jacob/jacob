from pyshould import it

from database.models import Storage
from database.utils import admin


class TestAdmin:
    def test_is_user_admin(self):

        test_student_id = 1

        status = admin.is_user_admin(test_student_id)

        it(status).should.be_equal(True)

    def test_is_non_admin_is_admin(self):

        test_student_id = 3

        status = admin.is_user_admin(test_student_id)

        it(status).should.be_equal(False)

    def test_get_admin_storage(self):

        test_student_id = 1

        store = admin.get_admin_storage(test_student_id)

        it(store).should.be_an_instance_of(Storage)

    def test_get_non_admin_storage(self):

        test_student_id = 3

        store = admin.get_admin_storage(test_student_id)

        it(store).should.be_an_instance_of(type(None))
