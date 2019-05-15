from clcrypto import password_hash
from datetime import datetime
from psycopg2 import connect
import os


db_username = os.environ.get('POSTGRES_USERNAME')
passwd = os.environ.get('POSTGRES_PASSWORD')
hostname = os.environ.get('POSTGRES_HOST')
db_name = os.environ.get('POSTGRES_DB_NAME')


def connector(func):
    """
    Connector function used as decorator to process all postgres DB connections.

    :param func: wrapped function
    :return: whatever wrapped function returns is saved to variable and returned by connector
    """
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
    """
    User class, used to process all inquiries to 'users' DB table.
    Methods which have cursor param in their method have to be used with @connector.
    """
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
        """
        Sets password to user - since password is private variable. Uses password_hash() to hash password.

        :param password: password to be set, string type
        :return: no return
        """
        self.__hashed_password = password_hash(password)

    def save_to_db(self, _cursor):
        """
        Saves user to DB. If user is not in DB then __id is -1. In this case function inserts new user.
        Otherwise it updates already existing user in DB

        :param _cursor: parameter passed with connector decorator
        :return:
        """
        if self.__id == -1:
            sql = """INSERT INTO Users(username, hashed_password)
                     VALUES(%s, %s) RETURNING id;"""
            values = (self.username, self.__hashed_password)
            _cursor.execute(sql, values)
            self.__id = _cursor.fetchone()[0]
            return True
        else:
                sql = """UPDATE Users SET username = %s, hashed_password = %s
                         WHERE id = %s;"""
                values = (self.username, self.__hashed_password, self.__id)
                _cursor.execute(sql, values)
        return False

    @staticmethod
    def loaded_user(data):
        """
        Creates User object with given data. Used with load - methods in this class.

        :param data: list of variables in this order [id, username, hashed_password]
        :return: User object if data is not None, otherwise None
        """
        if data:
            loaded_user = User()
            loaded_user.__id = data[0]
            loaded_user.username = data[1]
            loaded_user.__hashed_password = data[2]
            return loaded_user
        else:
            return None

    @staticmethod
    def load_user_by_username(_cursor, username):
        """
        Loads user by given username, users other staticmethod loaded_user()

        :param _cursor: parameter passed with connector decorator
        :param username: username which will be used in query, string type
        :return: User object if user has been found by query, otherwise None
        """
        sql = "SELECT id, username, hashed_password FROM users WHERE username=%s"
        _cursor.execute(sql, (username,))
        data = _cursor.fetchone()
        return User.loaded_user(data)
    
    @staticmethod
    def load_user_by_id(_cursor, user_id):
        """
        Load user by given id, uses other staticmethod loaded_user()

        :param _cursor: parameter passed with connector decorator
        :param user_id: user id which will be used in query, string type
        :return: User object if user has been found by query, otherwise None
        """
        sql = "SELECT id, username, hashed_password FROM users WHERE id=%s;"
        _cursor.execute(sql, (user_id,))
        data = _cursor.fetchone()
        return User.loaded_user(data)
    
    @staticmethod
    def load_all_users(_cursor):
        """
        Loads all users in DB. Goes one by one row and creates User object for each. Appends to all_users list.

        :param _cursor: parameter passed with connector decorator
        :return: list of User objects, each object is one user
        """
        sql = "SELECT id, username, hashed_password FROM Users;"
        all_users = list()
        _cursor.execute(sql)
        for row in _cursor.fetchall():
            all_users.append(User.loaded_user(row))
        return all_users
    
    def delete(self, _cursor):
        """
        Deletes user. Sets object __id to -1.

        :param _cursor: parameter passed with connector decorator
        :return: None
        """
        sql = "DELETE FROM Users WHERE id=%s;"
        _cursor.execute(sql, (self.__id,))
        self.__id = -1
        return None


class Message:
    """
    Message class, used to process all inquiries to 'messages' DB table.
    Methods which have cursor param in their method have to be used with @connector.
    """
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
        """
        __is_visible is a private parameter. It gives information if message is visible to recipient.
        Recipient can delete message - which makes __is_visible False. Message is still in DB and is visible for Sender.

        :return: __is_visible, boolean type
        """
        return self.__is_visible
    
    @property
    def creation_date(self):
        return self.__creation_date

    def recipient_delete_message(self):
        """
        'Deletes' message for recipient. It won't be visible for load_message queries for recipient.
        Still be visible for Sender.
        """
        self.__is_visible = False
    
    @staticmethod
    def load_message(data):
        """
        Creates Message object and populates it with given data.

        :param data: list of params in this order [id, text, from_id, to_id, is_visible, creation_date]
        :return: Message object if there is data, otherwise None
        """
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
    def load_message_by_id(_cursor, message_id):
        """
        Loads messsage of given id.

        :param _cursor: parameter passed with connector decorator
        :param message_id: id of message to be loaded, string type
        :return: Message object if query found message, otherwise None
        """
        sql = "SELECT id, text, from_id, to_id, is_visible, creation_date FROM Messages WHERE id=%s;"
        _cursor.execute(sql, (message_id,))
        data = _cursor.fetchone()
        return Message.load_message(data)
        
        
    @staticmethod
    def load_all_messages_for_user(_cursor, user_id):
        """
        Loads all messages which were sent to user. Checks if message is visible for user.
        For each message - one Message object is created and appended to list which is returned

        :param _cursor: parameter passed with connector decorator
        :param user_id: id of user which requests his messages to be loaded, string type
        :return: list of all Messages objects
        """
        all_messages = list()
        sql = "SELECT id, text, from_id, to_id, is_visible, creation_date FROM Messages WHERE to_id=%s;"
        _cursor.execute(sql, (user_id,))
        data = _cursor.fetchall()
        for row in data:
            message = Message.load_message(row)
            if message.is_visible:
                all_messages.append(message)
        return all_messages
    
    @staticmethod
    def load_all_messages_by_user(_cursor, user_id):
        """
        Loads all messages which user has sent.
        For each message - one Message object is created and appended to list which is returned

        :param _cursor: parameter passed with connector decorator
        :param user_id: id of user which requests his messages to be loaded, string type
        :return: list of all Messages objects
        """
        all_messages = list()
        sql = "SELECT id, text, from_id, to_id, is_visible, creation_date FROM Messages WHERE from_id=%s;"
        _cursor.execute(sql, (user_id,))
        data = _cursor.fetchall()
        for row in data:
            all_messages.append(Message.load_message(row))
        return all_messages
    
    def delete_by_sender(self, _cursor):
        """
        Deletes message which was sent by user. Unlike delete_by_recipient - this method deletes message from DB.
        Deletes message for sender and recipient as well in result.

        :param _cursor: parameter passed with connector decorator
        :return: None
        """
        sql = "DELETE FROM Messages WHERE id=%s;"
        _cursor.execute(sql, (self.id,))
        self.__id = -1
        return None     
    
    def save_to_db(self, _cursor):
        """
        Saves message to DB if message is new (id is -1). Otherwise it updates the message.

        :param _cursor: parameter passed with connector decorator
        :return:
        """
        if self.__id == -1:
            sql = """INSERT INTO Messages(text, from_id, to_id, is_visible, creation_date)
                     VALUES(%s, %s, %s, %s, %s) RETURNING id;"""
            values = (self.text, self.from_id, self.to_id, self.is_visible, self.creation_date)
            _cursor.execute(sql, values)
            self.__id = _cursor.fetchone()[0]
        else:
            sql = """UPDATE Messages SET text = %s, from_id = %s, to_id = %s, is_visible = %s
                         WHERE id=%s;"""
            values = (self.text, self.from_id, self.to_id, self.is_visible, self.id)
            _cursor.execute(sql, values)







