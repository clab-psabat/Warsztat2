-- no module docstring

from models import User, connector
from argparse import ArgumentParser
from clcrypto import is_password_correct
from helpers import load_user, args_to_be_empty, args_required, logging_user


@connector
def save_new_user(_cursor, username, password):
    """
    Saves new user to DB through User class. Strictly used with connector decorator.

    :param _cursor: parameter passed with connector decorator
    -- no descrption of what _cursor is
    :param username: username of new user, string type
    -- put type in :type username: clause
    :param password: password of new user, string type
    :return: Function has only one return if shield IF statement detects that password does not meet requirements.
    -- this function returns None always
    """
    if not is_password_correct(password):
        return
    user = User()
    user.username = username
    user.set_password(password)
    user.save_to_db(_cursor)
    print('New user created!')


@connector
def change_password(_cursor, user, new_password):
    """
    Changes password through User class. Strictly used with connector decorator.
    This function is launched only if main() finds given user in DB. Hence user param cannot be empty.
    -- you may assume here that user param is not empty, but don't assume that this function is called from main
    -- what is you refactor your code?

    :param _cursor: parameter passed with connector decorator
    :param user: User class object, loaded from DB.
    :param new_password: new password to be set, string type. Checked by IF statement
    -- as a user if change_password() function I don't have to know that you are using any IF to check it
    :return: as wrapped function has no return. Function prints only success statement
    -- it returns None
    -- printing should be described above, not in :return: line
    """
    if is_password_correct(new_password):
        user.set_password(new_password)
        user.save_to_db(_cursor)
        print('Password changed!')
    -- maybe some error or exception when password is incorrect?
    -- how can calling function know that this function failed to do it's work?

@connector
def delete_user(_cursor, user):
    """
    Deletes user through User class. Is launched by main() only if validation of username and password is successful.
    User parameter cannot be empty, otherwise main() won't launch this function.
    -- same comment about main() logic
    Used strictly with connector decorator

    :param _cursor: parameter passed with connector decorator
    :param user: User class object, loaded from DB
    :return: as wrapped function has no return. Function prints success statement
    -- it returns None
    -- printing should be described above, not in :return: line
    """
    user.delete(_cursor)
    print('user deleted!')


@connector
def load_all_users_in_db(_cursor):
    """
    Loads all users which are in DB through User class. Uses staticmethod from User class
    Used strictly with connector decorator

    :param _cursor: parameter passed with connector decorator
    :return: function has no return. Prints all users, pair of '{id}; {username}' in each line.
    -- it returns None
    -- printing should be described above, not in :return: line
    """
    users = User.load_all_users(_cursor)
    for user in users:
        print("id: {}; username: {}".format(user.id, user.username))


def main(parser):
    """
    Main function of program. Collects all arguments from parser parameter.
    Then loads User class object with given username.

    Scenarios:
        1. --username , --password are only given:
            a) Save new user - launches save_new_user() if load_user() returns None (no user with given username in DB)
            b) If user is in DB - print statement informing that more arguments have to be passed.
        2. --username, --password, --edit, --newpass are given:
            a) Changes password - launches change_password() only if logging_user() is successful.
            b) Returns None if logging has failed, logging_user() prints fail reason.
        3. --username, --password, --delete are given:
            a) Deletes user - launches delete_password() only if logging_user() is successful.
            b) Returns None if logging has failed, logging_user() prints fail reason.
        4. --list is given:
            Launches load_all_users_in_db() which prints all users in DB
        5. Else scenario:
            In any other case - function prints --help

    :param parser: ArgumentParser class. Created in set_parser_arguments()
    :return: function has no return
    -- it returns None
    """
    args = parser.parse_args()
    username = args.username
    password = args.password
    new_pass = args.newpass
    users_list = args.list
    delete = args.delete
    edit = args.edit

    user = load_user(username=username)

    -- description of scenarios should be in the code as described in review of messages.py
    # Scenario no. 1
    if args_required(username, password) and args_to_be_empty(new_pass, users_list, delete, edit):
        if not user:
            return save_new_user(username, password)
        else:
            print('Please add arguments, your query is empty')
            return

    # Scenario no. 2
    elif args_required(username, password, edit, new_pass) and args_to_be_empty(delete, users_list):
        if logging_user(user, password):
            return change_password(user, new_pass)
        else:
            return

    # Scenario no. 3
    elif args_required(username, password, delete) and args_to_be_empty(new_pass, users_list, edit):
        if logging_user(user, password):
            return delete_user(user)
        else:
            return

    # Scenario no. 4
    elif args_required(users_list) and args_to_be_empty(username, password, delete, edit, new_pass):
        return load_all_users_in_db()

    # Scenario no. 5
    else:
        -- print() and then parser.print_help() ?
        print("""You have used wrong arguments combination. See below scenarios:
        -u USERNAME -p PASSWORD | creates new user
        -u USERNAME -p PASSWORD -n NEWPASS -e | sets new password
        -u USERNAME -p PASSWORD -d | deletes user
        -l | prints all users
        For more see below""")
        return parser.print_help()


def set_parser_arguments():
    """
    Sets all parser arguments. If you want to add more - add in this function and then add scenario to main()

    :return: ArgumentParser class object which is used in main()
    """
    parser = ArgumentParser()
    parser.add_argument('-u', '--username', type=str,
                        help="your username"
                        )
    parser.add_argument('-p', '--password', type=str,
                        help='write your password to log in and use program features'
                        )
    parser.add_argument('-n', '--newpass', type=str,
                        help="changing your password. Only a-Z, 0-9 chars and min 8 chars long"
                        )
    parser.add_argument('-l', '--list',
                        help='show all users in database',
                        action="store_true"
                        )
    parser.add_argument('-d', '--delete',
                        help='delete your account. Only if login/pass validation is successful',
                        action='store_true'
                        )
    parser.add_argument('-e', '--edit',
                        help='edit your user profile - change password. Only a-Z, 0-9 chars and min 8 chars long',
                        action="store_true"
                        )
    return parser

-- add if __name__ == '__main__'
parser_args = set_parser_arguments()
main(parser_args)
