import hashlib
import random
import string

"""
ALPHABET is a global variable, that keeps all uppercase letter, all lowercase
letters and digits.
"""
ALPHABET = string.ascii_uppercase + string.ascii_lowercase + string.digits
PASSWORD_MIN_LENGTH = 8


def is_password_correct(password):
    """
    Check if password meets requirements.
    Standard requirements are passed through global variables
    Length and Alphabet (which chars are allowed)
    Prints errors

    :param password: password to be checked, string type
    :return: boolean - True if password meets requirements, False if not.
    """
    if len(password) < PASSWORD_MIN_LENGTH:
        print('New password is too short. Password has to be at least {} chars long'.format(PASSWORD_MIN_LENGTH))
        return False
    for char in password:
        if char not in ALPHABET:
            print('Wrong type of char in new pass. Acceptable chars are uppercase, lowercase letters and digits')
            return False
    return True


def generate_salt():
    """
    Generates a 16-character random salt.

    :return: str with generated salt
    """
    salt = ""
    for i in range(0, 16):
        salt += random.choice(ALPHABET)
    return salt


def password_hash(password, salt=None):
    """
    Hashes the password with salt as an optional parameter.
    If salt is not provided, generates random salt.
    If salt is less than 16 chars, fills the string to 16 chars.
    If salt is longer than 16 chars, cuts salt to 16 chars.
    """

    # generate salt if not provided
    if salt is None:
        salt = generate_salt()

    # fill to 16 chars if too short
    if len(salt) < 16:
        salt += ("a" * (16 - len(salt)))

    # cut to 16 if too long
    if len(salt) > 16:
        salt = salt[:16]

    # use sha256 algorithm to generate hash
    t_sha = hashlib.sha256()

    # we have to encode salt & password to utf-8, this is required by the
    # hashlib library.
    t_sha.update(salt.encode('utf-8') + password.encode('utf-8'))

    # return salt & hash joined
    return salt + t_sha.hexdigest()


def check_password(pass_to_check, hashed):
    """
    Checks the password.
    The function does the following:
        - gets the salt + hash joined,
        - extracts salt and hash,
        - hashes `pass_to_check` with extracted salt,
        - compares `hashed` with hashed `pass_to_check`.
        - returns True if password is correct, or False. :)
    """

    # extract salt
    salt = hashed[:16]

    # extract hash to compare with
    hash_to_check = hashed[16:]

    # hash password with extracted salt
    new_hash = password_hash(pass_to_check, salt)

    # compare hashes. If equal, return True
    if new_hash[16:] == hash_to_check:
        return True
    else:
        print('Logging error, wrong password. Try again')
        return False


