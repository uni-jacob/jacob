from database.models import Issue


def get_last_issue_of_user(vk_id: int):
    return (
        Issue.select().order_by(Issue.id.desc()).where(Issue.from_id == vk_id).limit(1)
    )
