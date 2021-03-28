import pytest
from pony import orm
from pyexpect import expect

from jacob.database.models import Group
from jacob.database.utils import admin
from jacob.services.exceptions import UserIsNotAnAdmin


class TestAdmin:
    def test_is_user_admin(self):

        test_student_id = 23

        status = admin.is_user_admin(test_student_id)

        expect(status).to.equal(True)

    def test_is_non_admin_is_admin(self):

        test_student_id = 3

        with pytest.raises(UserIsNotAnAdmin):
            admin.is_user_admin(test_student_id)

    def test_get_admin_feud(self):

        test_student_id = 23

        with orm.db_session:
            groups = admin.get_admin_feud(test_student_id)[:]

        expect(groups[0]).is_instance_of(Group)

    def test_get_admin_feud_of_non_admin(self):

        test_student_id = 24

        with orm.db_session:
            groups = admin.get_admin_feud(test_student_id)

        expect(groups).is_equal(None)

    def test_get_active_group(self):

        test_student_id = 23

        group = admin.get_active_group(test_student_id)

        expect(group).is_instance_of(Group)

    def test_get_active_group_of_non_admin(self):

        test_student_id = 24

        with pytest.raises(UserIsNotAnAdmin):
            admin.get_active_group(test_student_id)
