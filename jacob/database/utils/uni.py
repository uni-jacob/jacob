from pony.orm import db_session
from pony.orm import select

from database import models


@db_session
def get_all():
    return select(uni for uni in models.AlmaMater)[:]
