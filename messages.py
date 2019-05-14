from models import Message, connector
from argparse import ArgumentParser
from helpers import load_user, args_to_be_empty, args_required, logging_user


@connector
def load_user_messages(_cursor, user):
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
    message = Message().load_message_by_id(_cursor, message_id)
    if not message:
        print('Message ID not found, please check and try again')
    if message.to_id == user.id and message.is_visible:
        message.recipient_delete_message()
        message.save_to_db(_cursor)
        print('Message deleted!')
        return
    elif message.from_id == user.id:
        message.delete_by_sender(_cursor)
        print('Message deleted!')
        return


def message_main(parser):
    args = parser.parse_args()
    username = args.username
    password = args.password
    messages_list = args.list
    to_user = args.to
    message_text = args.send
    delete = args.delete

    user = load_user(username)
    if not user:
        print('Invalid login')
        return

    if args_required(username, password, messages_list) and args_to_be_empty(to_user, message_text, delete):
        if logging_user(user, password):
            return load_user_messages(user)

    elif args_required(username, password, to_user, message_text) and args_to_be_empty(messages_list, delete):
        if logging_user(user, password):
            return send_message(user, to_user, message_text)

    elif args_required(username, password, delete) and args_to_be_empty(messages_list, to_user, message_text):
        if logging_user(user, password):
            return delete_message(user, delete)

    else:
        print('Not enough arguments')


def set_parser_arguments():
    parser = ArgumentParser()
    parser.add_argument('-u', '--username', type=str, help='write your username')
    parser.add_argument('-p', '--password', type=str, help='write your password ')
    parser.add_argument('-l', '--list', help='list of all messages, send and received. you have to pass login and password',
                        action="store_true")
    parser.add_argument('-t', '--to', type=str, help='pass recipient username')
    parser.add_argument('-s', '--send', type=str, help='pass your message')
    parser.add_argument('-d', '--delete', type=str, help='delete message, pass message id')
    return parser


if __name__ == "__main__":
    parser = set_parser_arguments()
    message_main(parser)