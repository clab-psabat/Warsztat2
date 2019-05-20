-- module docstring describing why this file is for would be nice
"""Module which manages messages. User has to be logges successfuly to use this module functions
Main functions: loading messages sent by user and received as well, sending messages, deleting messages which user has access to - 
so either sent or received."""
from models import Message, connector
from argparse import ArgumentParser
from helpers import load_user, args_to_be_empty, args_required, logging_user


@connector
def load_user_messages(_cursor, user):
    """
    Loads all user messages, sent and received as well.
    Prints them into console, one message per line.
    Headlines are formatted with filler and specified width. 
    Each headline separates type of messages (sent/received)

    :param _cursor: parameter passed with connector decorator, it is a psycopg2 module cursor which implements
    changes to DB
    -- this description tells from where to get given parameter
    -- it still does not say what this parameter is, what is does
    -- the same goes for all docstrings in all functions
    :param user: User model which is loaded from DB
    -- you cannot assume that some function will *always* be called by some other specific function
    :type _cursor: class; psycopg2.extensions.cursor
    :type user: models.User class
    :return: None
    -- it either returns None or sth, telling that is prints in descrption of return statement is unnecessary
    """
    headline_width = 40
    headline_filler_symbol = '-'
    sent_messages = Message.load_all_messages_by_user(_cursor, user.id)
    received_messages = Message.load_all_messages_for_user(_cursor, user.id)
    print("Sent messages".center(headline_width, headline_filler_symbol))
    -- nice formatting function, I didn't know it exists :)
    -- lots of codewars challenges is finally giving profits :) 
    for message in sent_messages:
        print("id: {}; sent to: {};\nTime: {}\nMessage: {}\n".format(message.id,
                                                                     message.to_id,
                                                                     message.creation_date,
                                                                     message.text))
        print('-'*40)
    print("Received messages".center(headline_width, headline_filler_symbol))
    for message in received_messages:
        print("id: {}; from: {};\nTime: {}\nMessage: {}\n".format(message.id,
                                                                  message.from_id,
                                                                  message.creation_date,
                                                                  message.text))
        print(headline_filler_symbol * headline_width)
        -- you are using the same number 40 a few times, perhaps you would like to move it to some variable with
        -- some meaningful name
        -- great advice, thank you, 101 clean code :) 


@connector
def send_message(_cursor, user, to_user, message_text):
    """
    Sends message using Message-class methods.
    -- again don't assume being called by main()

    :param _cursor: parameter passed with connector decorator, it is a psycopg2 module cursor which implements
    changes to DB
    :param user: User model which is loaded from DB, creator and sender of message
    :param to_user: recipient user id
    -- you can tell type of parameter by typing :type to_user: string
    :param message_text: message text
    :type _cursor: class; psycopg2.extensions.cursor
    :type user: models.User class
    :type to_user: str
    :type message: str
    :return: None
    -- function prints, but what does it return?
    """
    recipient = load_user(id=to_user)
    if not recipient:
        print('Recipient ID not found, please check and try again')
        return
    new_message = Message()
    new_message.to_id = recipient.id
    new_message.text = message_text
    new_message.from_id = user.id
    new_message.save_to_db(_cursor)
    -- sending a message is by saving it to a databse? this looks very unintuitive. can it be resolved somehow?
    print('Message sent!')


@connector
def delete_message(_cursor, user, message_id):
    """
    Deletes message of given ID. It has 4 scenarios, which are described in function body.

    :param _cursor: parameter passed with connector decorator, it is a psycopg2 module cursor which implements
    changes to DB
    :param user: User model which is loaded from DB, user which request delete message
    :param message_id: message ID to be deleted
    :type _cursor: class; psycopg2.extensions.cursor
    :type user: models.User class
    :type message_id: str
    :return: None
    -- return does not print
    """
    message = Message().load_message_by_id(_cursor, message_id)

    
    -- scenarios are described in docstring, but when you add or remove a scenario, then you must modify
    -- sourcecode in two places. thus it is better to keep description of scenarios directly in code as comments
    """ Scenario no. 1  Message ID is not valid.
                Function did not find such message. Prints fail statement."""
    if not message:
        print('Message ID not found, please check and try again')

    """ Scenario no. 2  User requesting deletion is Recipient and message is visibe for him
                Function uses Message static method to make message invisible for Recipient. Sender still can see it."""
    if message.to_id == user.id and message.is_visible:
        message.recipient_delete_message()
        message.save_to_db(_cursor)
        print('Message deleted!')
        return

    """ Scenario no. 3 User requesting deletion is Sender
                Function uses Message method to delete message. It will be deleted also for Recipient."""
    elif message.from_id == user.id:
        message.delete_by_sender(_cursor)
        print('Message deleted!')
        return

    """ Scenario no. 4 User is neither Sender nor Recipient
                Function prints fail statement."""
    else:
        print('You cannot delete this message, you are not sender nor recipient')


def main(parser):
    """
    Main function of program. Collects all arguments from parser parameter.
    Then loads User class object with given username.
    Function has 4 scenarios which are described in function body. 

    Preconditions:
        1. Checks if given username is in DB, if not user is None
        2. Try to log in user. Stops function if false (logging_user() prints fail statements)

    :param parser: ArgumentParser class. Created in set_parser_arguments()
    :return: depends on scenario - returns requested function
    """
    args = parser.parse_args()
    username = args.username
    password = args.password
    messages_list = args.list
    to_user = args.to
    message_text = args.send
    delete = args.delete

    user = load_user(username)

    # Preconditions
    -- you probably meant preconditions, eventually asserts
    if not user:
        print('Invalid login')
        return
    if logging_user(user, password) is False:
        print('Invalid password for given username')
        -- no error message for a user?
        return

    -- same comment about scenarios as above
    """ Scenario no. 1 --username , --password -l are given:
            List all messages which were sent by user and messages which he received (and did not delete)"""
    if args_required(username, password, messages_list) and args_to_be_empty(to_user, message_text, delete):
        return load_user_messages(user)

    """ Scenario no. 2 --username, --password, --to, --send are given:
            Sends message to target user"""
    elif args_required(username, password, to_user, message_text) and args_to_be_empty(messages_list, delete):
        return send_message(user, to_user, message_text)

    """ Scenario no. 3 --username, --password, --delete are given:
            Deletes message. Has 4 scenarios - depending who is calling this method. For details see delete_message() docstring"""
    elif args_required(username, password, delete) and args_to_be_empty(messages_list, to_user, message_text):
        return delete_message(user, delete)

    """ Scenario no. 4 Else scenario:
            In any other case - function prints --help"""
    else:
        -- printing help manually and then calling parser.print_help() seems a bit too much
        return parser.print_help()


def set_parser_arguments():
    """
    Sets all parser arguments. If you want to add more - add in this function and then add scenario to main()

    :return: ArgumentParser class object
    -- where this object is used is of no concern for this function
    """
    parser = ArgumentParser()
    parser.add_argument('-u', '--username', type=str, help='write your username')
    parser.add_argument('-p', '--password', type=str, help='write your password ')
    parser.add_argument('-l', '--list', help='list of all messages, send and received',
                        action="store_true")
    parser.add_argument('-t', '--to', type=str, help='pass recipient id')
    parser.add_argument('-s', '--send', type=str, help='pass your message')
    parser.add_argument('-d', '--delete', type=str, help='delete message, pass message id')
    return parser

-- adding if __name__ == '__main__' mantra would be nice here
if __name__ == '__main__':
    parser_args = set_parser_arguments()
    main(parser_args)
