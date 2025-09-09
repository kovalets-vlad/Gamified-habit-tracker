import operator
from ..db.models import Streak, User

OPS = {
    ">=": operator.ge,
    "<=": operator.le,
    ">": operator.gt,
    "<": operator.lt,
    "==": operator.eq,
}

def check_condition(cond: dict, streak: Streak, user: User) -> bool:
    field = cond.get("field")
    op = OPS.get(cond.get("operator"))
    value = cond.get("value")

    if not field or not op or value is None:
        return False

    if field == "streak":
        return op(streak.current_streak, value)
    elif field == "xp":
        return op(user.xp, value)
    elif field == "level":
        return op(user.level, value)
    return False
