from models import User
from psycopg2 import connect

username = 'postgres'
passwd = 'coderslab'
hostname = '127.0.0.1'
db_name = 'message_server'


new_user = User()
new_user.username = 'jaco'
new_user.email = 'jaco@placo.pl'
new_user.set_password('cowabunga')


db_conn = connect(user='postgres', password='coderslab', host='127.0.0.1', database='message_server')
db_conn.autocommit = True
db_curr = db_conn.cursor()

new_user.save_to_db(db_curr)

db_curr.close()
db_conn.close()