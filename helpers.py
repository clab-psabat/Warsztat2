from models import User, connector
from clcrypto import check_password

# Functions here are user by both programs, users and messages. Stored here to have more control over them

@connector
def load_user(_cursor, username=None, id=None):
    """
    Loads User class object using User static methods.
    Depends which argument is passed, it will either load by username or by id.

    :param _cursor: parameter passed with connector decorator
    :param username: optional argument, string type.
    :param id: optional argument, string type.
    :return: User class object - regardless of optional argument choice. If no arguments passed - it will return None
    """
    if username:
        return User().load_user_by_username(_cursor, username)
    elif id:
        return User().load_user_by_id(_cursor, id)
    else:
        return None


def args_required(*args):
    """
    Strictly used with parser arguments. Loops through given arguments and checks which are empty.
    Since all arguments passed have to be not None - once it will find such argument - it stops and returns False

    :param args: parser arguments passed by main() from users or messages program
    :return: True if all args passed are not None, otherwise False
    """
    for arg in args:
        if not arg:
            return False
    return True


def args_to_be_empty(*args):
    """
    Strictly used with parser arguments.
    Functionality similar like args_required() only difference is that arguments passed have to be None.

    :param args: parser arguments passed by main() from users or messages program
    :return: True is all args passed are None, otherwise False
    """
    for arg in args:
        if arg:
            return False
    return True


def logging_user(user, password):
    """
    Validates given password with user password saved in DB

    :param user: User class object
    :param password: password user in log in, string type. Passed through parser
    :return: True if password matches user password, otherwise False. Also False if user is None
    """
    if not user:
        print('No such user in database')
        return False
    elif not check_password(password, user.hashed_password):
        return False
    return True
