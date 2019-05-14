from clcrypto import password_hash
from datetime import datetime
from psycopg2 import connect
import os


db_username = os.environ.get('POSTGRES_USERNAME')
passwd = os.environ.get('POSTGRES_PASSWORD')
hostname = os.environ.get('POSTGRES_HOST')
db_name = os.environ.get('POSTGRES_DB_NAME')


def connector(func):
    def wrapper(*args, **kwargs):
        cnx = connect(user=db_username,
                      password=passwd,
                      host=hostname,
                      database=db_name)
        _cursor = cnx.cursor()
        operation = func(_cursor, *args, **kwargs)
        cnx.commit()
        _cursor.close()
        cnx.close()
        return operation

    return wrapper


class User:
    __id = None
    username = None
    __hashed_password = None

    def __init__(self):
        self.__id = -1
        self.username = ""
        self.__hashed_password = ""

    @property
    def id(self):
        return self.__id

    @property
    def hashed_password(self):
        return self.__hashed_password

    def set_password(self, password):
        self.__hashed_password = password_hash(password)

    def save_to_db(self, cursor):
        if self.__id == -1:
            sql = """INSERT INTO Users(username, hashed_password)
                     VALUES(%s, %s) RETURNING id;"""
            values = (self.username, self.__hashed_password)
            cursor.execute(sql, values)
            self.__id = cursor.fetchone()[0]
            return True
        else:
                sql = """UPDATE Users SET username = %s, hashed_password = %s
                         WHERE id = %s;"""
                values = (self.username, self.__hashed_password, self.__id)
                cursor.execute(sql, values)
        return False
    
    @staticmethod
    def loaded_user(data):
        if data:
            loaded_user = User()
            loaded_user.__id = data[0]
            loaded_user.username = data[1]
            loaded_user.__hashed_password = data[2]
            return loaded_user
        else:
            return None

    @staticmethod
    def load_user_by_username(cursor, username):
        sql = "SELECT id, username, hashed_password FROM users WHERE username=%s"
        cursor.execute(sql, (username,))
        data = cursor.fetchone()
        return User.loaded_user(data)
    
    @staticmethod
    def load_user_by_id(cursor, user_id):
        sql = "SELECT id, username, hashed_password FROM users WHERE id=%s;"
        cursor.execute(sql, (user_id,))
        data = cursor.fetchone()
        return User.loaded_user(data)
    
    @staticmethod
    def load_all_users(cursor):
        sql = "SELECT id, username, hashed_password FROM Users;"
        all_users = list()
        cursor.execute(sql)
        for row in cursor.fetchall():
            all_users.append(User.loaded_user(row))
        return all_users
    
    def delete(self, cursor):
        sql = "DELETE FROM Users WHERE id=%s;"
        cursor.execute(sql, (self.__id,))
        self.__id = -1
        return None


class Message:
    __id = None
    text = None
    from_id = None
    to_id = None
    __is_visible = None
    __creation_date = None 

    def __init__(self):
        self.__id = -1
        self.text = ""
        self.from_id = ""
        self.to_id = ""
        self.__is_visible = True
        self.__creation_date = datetime.utcnow()
    
    @property
    def id(self):
        return self.__id
    
    @property
    def is_visible(self):
        return self.__is_visible
    
    @property
    def creation_date(self):
        return self.__creation_date

    def recipient_delete_message(self):
        self.__is_visible = False
    
    @staticmethod
    def load_message(data):
        if data:
            loaded_message = Message()
            loaded_message.__id = data[0]
            loaded_message.text = data[1]
            loaded_message.from_id = data[2]
            loaded_message.to_id = data[3]
            loaded_message.__is_visible = data[4]
            loaded_message.__creation_date = data[5]
            return loaded_message
        else:
            return None
    
    @staticmethod
    def load_message_by_id(cursor, message_id):
        sql = "SELECT id, text, from_id, to_id, is_visible, creation_date FROM Messages WHERE id=%s;"
        cursor.execute(sql, (message_id,))
        data = cursor.fetchone()
        return Message.load_message(data)
        
        
    @staticmethod
    def load_all_messages_for_user(cursor, user_id):
        all_messages = list()
        sql = "SELECT id, text, from_id, to_id, is_visible, creation_date FROM Messages WHERE to_id=%s;"
        cursor.execute(sql, (user_id,))
        data = cursor.fetchall()
        for row in data:
            message = Message.load_message(row)
            if message.is_visible:
                all_messages.append(message)
        return all_messages
    
    @staticmethod
    def load_all_messages_by_user(cursor, user_id):
        all_messages = list()
        sql = "SELECT id, text, from_id, to_id, is_visible, creation_date FROM Messages WHERE from_id=%s;"
        cursor.execute(sql, (user_id,))
        data = cursor.fetchall()
        for row in data:
            all_messages.append(Message.load_message(row))
        return all_messages
    
    def delete_by_sender(self, cursor):
        sql = "DELETE FROM Messages WHERE id=%s;"
        cursor.execute(sql, (self.id,))
        self.__id = -1
        return None     
    
    def save_to_db(self, cursor):
        if self.__id == -1:
            sql = """INSERT INTO Messages(text, from_id, to_id, is_visible, creation_date)
                     VALUES(%s, %s, %s, %s, %s) RETURNING id;"""
            values = (self.text, self.from_id, self.to_id, self.is_visible, self.creation_date)
            cursor.execute(sql, values)
            self.__id = cursor.fetchone()[0]
            return True
        else:
            sql = """UPDATE Messages SET text = %s, from_id = %s, to_id = %s, is_visible = %s
                         WHERE id=%s;"""
            values = (self.text, self.from_id, self.to_id, self.is_visible, self.id)
            cursor.execute(sql, values)
        return False







