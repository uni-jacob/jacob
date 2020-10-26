from pyshould import it
from pyshould.expect import expect_all

from database.models import Group
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

    def test_get_admin_feud(self):

        test_student_id = 1

        groups = admin.get_admin_feud(test_student_id)

        expect_all(groups).be_an_instance_of(Group)

    def test_get_admin_feud_of_non_admin(self):

        test_student_id = 3

        groups = admin.get_admin_feud(test_student_id)

        it(groups).should.be_equal([])

    def test_get_admin_storage(self):

        test_student_id = 1

        store = admin.get_admin_storage(test_student_id)

        it(store).should.be_an_instance_of(Storage)

    def test_get_non_admin_storage(self):

        test_student_id = 3

        store = admin.get_admin_storage(test_student_id)

        it(store).should.be_an_instance_of(type(None))

    def test_get_active_group(self):

        test_student_id = 1

        group = admin.get_active_group(test_student_id)

        it(group).should.be_equal(Group.get_by_id(2))

    def test_get_active_group_of_non_admin(self):

        test_student_id = 3

        group = admin.get_active_group(test_student_id)

        it(group).should.be_equal(None)
