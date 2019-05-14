from models import User, connector
from clcrypto import check_password


@connector
def load_user(_cursor, username=None, id=None):
    if username:
        return User().load_user_by_username(_cursor, username)
    elif id:
        return User().load_user_by_id(_cursor, id)
    else:
        return None


def args_required(*args):
    for arg in args:
        if not arg:
            return False
    return True


def args_to_be_empty(*args):
    for arg in args:
        if arg:
            return False
    return True


def logging_user(user, password):
    if not user:
        print('No such user in database')
        return False
    elif not check_password(password, user.hashed_password):
        return False
    return True
