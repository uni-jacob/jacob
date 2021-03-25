from pony import orm

from jacob.database import models


@orm.db_session
def get_lists_of_group(group_id: int):
    return orm.select(gr for gr in models.List if gr.group.id == group_id)
