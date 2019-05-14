from models import User, connector
from argparse import ArgumentParser
from clcrypto import is_password_correct
from helpers import load_user, args_to_be_empty, args_required, logging_user

@connector
def save_new_user(_cursor, username, password):
    if not is_password_correct(password):
        return
    user = User()
    user.username = username
    user.set_password(password)
    user.save_to_db(_cursor)
    print('New user created!')


@connector
def change_password(_cursor, user, new_password):
    if is_password_correct(new_password):
        user.set_password(new_password)
        user.save_to_db(_cursor)
        print('Password changed!')



@connector
def delete_user(_cursor, user):
    user.delete(_cursor)
    print('user deleted!')


@connector
def load_all_users_in_db(_cursor):
    users = User.load_all_users(_cursor)
    for user in users:
        print("id: {} ; username: {}".format(user.id, user.username))


@connector
def create_new_user(_cursor, username, password, email):
    new_user=User()
    new_user.username = username
    new_user.set_password(password)
    new_user.email = email
    new_user.save_to_db(_cursor)





def user_main(parser):
    args = parser.parse_args()
    username = args.username
    password = args.password
    new_pass = args.newpass
    users_list = args.list
    delete = args.delete
    edit = args.edit

    user = load_user(username=username)

    if args_required(username, password) and args_to_be_empty(new_pass, users_list, delete, edit):
        if not user:
            return save_new_user(username, password)
        else:
            print('Please add arguments, your query is empty')
            return

    elif args_required(username, password, edit, new_pass) and args_to_be_empty(delete, users_list):
        if logging_user(user, password):
            return change_password(user, new_pass)
        else:
            return

    elif args_required(username, password, delete) and args_to_be_empty(new_pass, users_list, edit):
        if logging_user(user, password):
            return delete_user(user)
        else:
            return

    elif args_required(users_list):
        return load_all_users_in_db()

    else:
        print('help')


def set_parser_arguments():
    parser = ArgumentParser()
    parser.add_argument('-u', '--username', type=str, help="""write your login/username as argument. If username is
                                                              not in database and -p argument used as well program 
                                                              will create new user.""")
    parser.add_argument('-p', '--password', type=str, help='write your password to log in and use program features')
    parser.add_argument('-n', '--newpass', type=str, help="""changing your password. Only if login/pass validation is
                                                           successful""")
    parser.add_argument('-l', '--list', help='show all users in database', action="store_true")
    parser.add_argument('-d', '--delete', help='delete your account. Only if login/pass validation is successful',
                        action='store_true')
    parser.add_argument('-e', '--edit', help='edit your user profile - change password. User -n parameter to pass new password',
                        action="store_true")
    return parser


parser = set_parser_arguments()
user_main(parser)