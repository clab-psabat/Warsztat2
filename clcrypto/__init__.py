import hashlib
import random
import string

"""
ALPHABET is a global variable, that keeps all uppercase letter, all lowercase
letters and digits.
"""
ALPHABET = string.ascii_uppercase + string.ascii_lowercase + string.digits


def generate_salt():
    """
    Generates a 16-character random salt.
    :return: str with generated salt
    """
    salt = ""
    for i in range(0, 16):

        # get a random element from the iterable
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
        return False


salt=generate_salt()
print(salt)

my_pass = "alamakota1"
my_pass_hashed = password_hash(my_pass, salt)
print(my_pass_hashed)

check = check_password("alamakota1", my_pass_hashed)
print(check)


salt = generate_salt()
print(salt)
passwd = password_hash('qwer234!', generate_salt())
print(passwd)

print(check_password('qwer234!', 'hzLHdLiAdbz5LgNI3383d71a6a80ec86671a8e1e3e76195152914982f70b7ec0f25e8dd1f9a7e4e7'))
print(check_password('qwer234!', 'elsIwi6cBJE21GWc4b62fbe586158f1f56fa68b3137b2526bfdc2567dd7f03d7390409eae306f7a7'))
print(check_password('qwer234!', passwd))