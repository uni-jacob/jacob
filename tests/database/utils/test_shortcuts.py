from pyshould import it

from database.utils import shortcuts


class TestShortcuts:
    def test_get_list_of_calling_students(self):

        test_admin_id = 1

        res = shortcuts.get_list_of_calling_students(test_admin_id)

        it(res).should.be_equal([1, 2, 3])

    def test_pop_student_from_calling_list(self):

        test_admin_id = 1
        test_student_id = 3

        res = shortcuts.pop_student_from_calling_list(test_admin_id, test_student_id)
        data = list(map(int, res.selected_students.split(",")))
        it(data).should.be_equal([1, 2])

    def test_add_student_to_calling_list(self):

        test_admin_id = 1
        test_student_id = 3

        res = shortcuts.add_student_to_calling_list(test_admin_id, test_student_id)
        data = list(map(int, res.selected_students.split(",")))
        it(data).should.be_equal([1, 2, 3])
