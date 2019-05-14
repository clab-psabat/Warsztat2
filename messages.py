from models import User, Message, connector
from argparse import ArgumentParser
from clcrypto import password_hash, check_password


def set_parser_arguments():
    parser = ArgumentParser()
    parser.add_argument('-u', '--username', type=str, help="""write your login/username as argument. If username is
                                                              not in database and -p argument used as well program 
                                                              will create new user.""")
    parser.add_argument('-p', '--password', type=str, help='write your password to log in and use program features')
    parser.add_argument('-n', '--new-pass', type=str, help="""changing your password. Only if login/pass validation is
                                                           successful""")
    parser.add_argument('-l', '--list', help='show all users in database', action="store_true")
    parser.add_argument('-d', '--delete', help='delete your account. Only if login/pass validation is successful')
    parser.add_argument('-e', '--edit', type=str, help='change your username')
    return parser


@connector
def create_new_user(_cursor, username, password, email):
    new_user=User()
    new_user.username = username
    new_user.set_password(password)
    new_user.email = email
    new_user.save_to_db(_cursor)


parser = set_parser_arguments()
parser.parse_args()
create_new_user("test3", "test3", "test3@test.com")

"""
db_conn = connect(user='postgres', password='coderslab', host='127.0.0.1', database='message_server')
db_conn.autocommit = True
db_curr = db_conn.cursor()



db_curr.close()
db_conn.close()
"""
