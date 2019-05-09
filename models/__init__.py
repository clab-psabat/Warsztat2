
from clcrypto import password_hash, check_password
form datetime import datetime


class User:
    __id = None
    username = None
    __hashed_password = None
    email = None

    def __init__(self):
        self.__id = -1
        self.username = ""
        self.email = ""
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
            sql = """INSERT INTO Users(username, email, hashed_password)
                     VALUES(%s, %s, %s) RETURNING id"""
            values = (self.username, self.email, self.hashed_password)
            cursor.execute(sql, values)
            self.__id = cursor.fetchone()[0]
            return True
        else:
                sql = """UPDATE Users SET username=%s, email=%s, hashed_password=%s
                         WHERE id = %s """
                values = (self.username, self.email, self.hashed_password, self.__id)
                cursor.execute(sql, values)
        return False
    
    @staticmethod
    def load_user(data):
         if data:
            loaded_user = User()
            loaded_user.__id = data[0]
            loaded_user.username = data[1]
            loaded_user.email = data[2]
            loaded_user.__hashed_password = data[3]
            return loaded_user
        else:
            return None
    
    @staticmethod
    def load_user_by_id(cursor, user_id):
        sql = "SELECT id, username, email, hashed_password FROM users WHERE id=%s"
        cursor.execute(sql, (user_id,))
        data = cursor.fetchone()
        return load_user(data)
    
    @staticmethod
    def load_all_users(cursor):
        sql = "SELECT id, username, email, hashed_password FROM Users"
        all_users = list()
        cursor.execute(sql)
        for row in cursor.fetchall():
            all_users.append(load_user(row))
        return all_users
    
    def delete(self, cursor):
        sql = "DELETE FROM Users WHERE id=%s"
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
        self.__creation_date = datetime.utcnow
    
    @property
    def id(self):
        return self.__id
    
    @property
    def is_visible(self):
        return self.__is_visible
    
    @property
    def creation_date(self):
        return self.__creation_date
    
    @staticmethod
    def load_message(data):
        if data:
            loaded_message = Message()
            loaded_mesage.__id = data[0]
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
        sql = "SELECT id, text, from_id, to_id, is_visible, creation_date FROM Messages WHERE id=%s"
        cursor.execute(sql, (message_id,))
        data = cursor.fetchone()
        return load_message(data)
        
        
    @staticmethod
    def load_all_messages_for_user(cursor, user_id):
        all_messages = list()
        sql = "SELECT id, text, from_id, to_id, is_visible, creation_date FROM Messages WHERE to_id=%s"
        cursor.execute(sql, (user_id,))
        data = cursor.fetchall()
        for row in data:
            all_messages.append(load_message(row))
        return all_messages
    
    @staticmethod
    def load_all_messages_by_user(cursor, user_id):
        all_messages = list()
        sql = "SELECT id, text, from_id, to_id, is_visible, creation_date FROM Messages WHERE from_id=%s"
        cursor.execute(sql, (user_id,))
        data = cursor.fetchall()
        for row in data:
            all_messages.append(load_message(row))
        return all_messages
    
    def delete_by_sender(self, cursor):
        sql = "DELETE FROM Messages WHERE id=%s"
        cursor.execute(sql, (self.__id,))
        self.__id = -1
        return None     
    
    def save_to_db(self, cursor):
        if self.__id == -1:
            sql = """INSERT INTO Messages(text, from_id, to_id, is_visible, creation_date)
                     VALUES(%s, %s, %s, %s, %s) RETURNING id"""
            values = (self.text, self.from_id, self.to_id, self.__is_visible, self.__creation_date)
            cursor.execute(sql, values)
            self.__id = cursor.fetchone()[0]
            return True
        else:
                sql = """UPDATE Messages SET text=%s, from_id=%s, to_id=%s, is_visible=%s,
                         WHERE id = %s"""
                values = (self.text, self.from_id, self.to_id, self.__is_visible, self.__id))
                cursor.execute(sql, values)
        return False
    
    
        
        
        
        
        
    
