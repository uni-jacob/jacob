import pytest
from pyshould import it

from services.exceptions import BotStateNotFound
from services.exceptions import UserIsNotAnAdministrator


class TestDatabaseUtils:
    def test_get_system_id_of_existing_student(self):
        from database.utils import get_system_id_of_student

        test_student_id = 549350532

        student_id = get_system_id_of_student(test_student_id)

        it(student_id).should.be_equal(1)

    def test_get_system_id_of_non_existing_student(self):
        from database.utils import get_system_id_of_student
        from services.exceptions import StudentNotFound

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

    def test_get_id_of_state(self):
        from database.utils import get_id_of_state

        test_description = "wait_call_text"

        state = get_id_of_state(test_description)

        it(state).should.be_equal(2)

    def test_get_id_of_non_existing_state(self):
        from database.utils import get_id_of_state

        test_description = "qwerty"

        with pytest.raises(BotStateNotFound):
            get_id_of_state(test_description)

    def test_get_unique_second_name_letters_in_a_group(self):
        from database.utils import get_unique_second_name_letters_in_a_group

        test_user_id = 549350532

        snd_names = get_unique_second_name_letters_in_a_group(test_user_id)

        it(snd_names).should.be_equal(["f", "Г"])

    def test_get_list_of_students_by_letter(self):
        from database.utils import get_list_of_students_by_letter
        from database.models import Student

        test_letter = "Г"
        test_user_id = 549350532
        test_student = Student.get(id=1)

        students = get_list_of_students_by_letter(test_letter, test_user_id)

        it(students).should.be_equal([test_student])

    def test_get_cached_chats(self):
        from database.utils import get_cached_chats
        from database.models import CachedChat

        test_cached_chat = CachedChat.get(id=1)

        cache = get_cached_chats()
        it(cache).should.be_equal([test_cached_chat])

    def test_is_chat_registered(self):
        from database.utils import is_chat_registered

        test_user_id = 549350532

        res = is_chat_registered(test_user_id, 1)

        it(res).should.be_equal(True)

    def test_get_list_of_calling_students(self):
        from database.utils import get_list_of_calling_students

        test_admin_id = 1

        res = get_list_of_calling_students(test_admin_id)

        it(res).should.be_equal([1, 2, 3])
