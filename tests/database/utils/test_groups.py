from pyshould import it

from database.models import Group
from database.utils.groups import find_group


class TestGroups:
    def test_find_group(self):
        group_id = 1
        group = Group.get(id=group_id)

        res = find_group(id=group_id)

        it(res).should.be_equal(group)
