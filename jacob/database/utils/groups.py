from pony import orm

from jacob.database import models


@orm.db_session
def get_academic_statuses_in_group(group_id: int) -> list:
    return orm.select(
        st.academic_status for st in models.Student if st.group.id == group_id
    )[:]


@orm.db_session
def get_subgroups_in_group(group_id: int) -> list:
    return orm.select(st.subgroup for st in models.Student if st.group.id == group_id)[
        :
    ]
