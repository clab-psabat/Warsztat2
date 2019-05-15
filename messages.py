from models import Message, connector
from argparse import ArgumentParser
from helpers import load_user, args_to_be_empty, args_required, logging_user


@connector
def load_user_messages(_cursor, user):
    """
    Loads all user messages, sent and received as well.
    Prints them into console, one message per line.

    :param _cursor: parameter passed with connector decorator
    :param user: User class object , passed by main()
    :return: function has no return. Prints all messages into console instead.
    """
    sent_messages = Message.load_all_messages_by_user(_cursor, user.id)
    received_messages = Message.load_all_messages_for_user(_cursor, user.id)
    print("Sent messages".center(40, '-'))
    for message in sent_messages:
        print("id: {}; sent to: {};\nTime: {}\nMessage: {}\n".format(message.id,
                                                                     message.to_id,
                                                                     message.creation_date,
                                                                     message.text))
        print('-'*40)
    print("Received messages".center(40, '-'))
    for message in received_messages:
        print("id: {}; from: {};\nTime: {}\nMessage: {}\n".format(message.id,
                                                                  message.from_id,
                                                                  message.creation_date,
                                                                  message.text))
        print('-' * 40)


@connector
def send_message(_cursor, user, to_user, message_text):
    """
    Sends message using Message-class methods. Launched by main().

    :param _cursor: parameter passed with connector decorator
    :param user: User class object , passed by main()
    :param to_user: recipient user id, string type
    :param message_text: message text, string type
    :return: function prints success statement if message is sent
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
    print('Message sent!')


@connector
def delete_message(_cursor, user, message_id):
    """
    Deletes message of given ID. It has 4 scenarios:

    Scenarios:
        1. Message ID is not valid.
                Function did not find such message. Prints fail statement.
        2. User requesting deletion is Recipient and message is visibe for him
                Function uses Message static method to make message invisible for Recipient. Sender still can see it.
        3. User requesting deletion is Sender
                Function uses Message method to delete message. It will be deleted also for Recipient
        4. User is neither Sender nor Recipient
                Function prints fail statement

    :param _cursor: parameter passed with connector decorator
    :param user: User class object , user which request delete message
    :param message_id: message ID to be deleted, string type
    :return: function has no return, prints fail/success statemetns
    """
    message = Message().load_message_by_id(_cursor, message_id)

    # Scenario no. 1
    if not message:
        print('Message ID not found, please check and try again')

    # Scenario no. 2
    if message.to_id == user.id and message.is_visible:
        message.recipient_delete_message()
        message.save_to_db(_cursor)
        print('Message deleted!')
        return

    # Scenario no. 3
    elif message.from_id == user.id:
        message.delete_by_sender(_cursor)
        print('Message deleted!')
        return

    # Scenario no. 4
    else:
        print('You cannot delete this message, you are not sender nor recipient')


def main(parser):
    """
    Main function of program. Collects all arguments from parser parameter.
    Then loads User class object with given username.

    Shield conditions:
        1. Checks if given username is in DB, if not user is None
        2. Try to log in user. Stops function if false (logging_user() prints fail statements)

    Scenarios:
        1. --username , --password -l are given:
            List all messages which were sent by user and messages which he received (and did not delete)
        2. --username, --password, --to, --send are given:
            Sends message to targer user
        3. --username, --password, --delete are given:
            Deletes message
        4. Else scenario:
            In any other case - function prints --help


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

    # Shield conditions
    if not user:
        print('Invalid login')
        return
    if logging_user(user, password) is False:
        return

    # Scenario no. 1
    if args_required(username, password, messages_list) and args_to_be_empty(to_user, message_text, delete):
        return load_user_messages(user)

    # Scenario no. 2
    elif args_required(username, password, to_user, message_text) and args_to_be_empty(messages_list, delete):
        return send_message(user, to_user, message_text)

    # Scenario no. 3
    elif args_required(username, password, delete) and args_to_be_empty(messages_list, to_user, message_text):
        return delete_message(user, delete)

    # Scenario no. 4
    else:
        print("""You have used wrong arguments combination. See below scenarios:
        -u USERNAME -p PASSWORD -l | lists all messages, sent and received
        -u USERNAME -p PASSWORD -to TO -s SEND| sends new message -to target user id with -s message text
        -u USERNAME -p PASSWORD -d | deletes message with ID passed in -d argument
        For more see below""")
        return parser.print_help()


def set_parser_arguments():
    """
    Sets all parser arguments. If you want to add more - add in this function and then add scenario to main()

    :return: ArgumentParser class object which is used in main()
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


parser_args = set_parser_arguments()
main(parser_args)