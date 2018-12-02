# Nate Verlin
# ChatChain
# File: store_and_sanitize.py
# This file is designed to provide some basic utility functions for the chat chain program. This includes:
#           - Sanitizing Input (is the input valid ascii)
#           - Storing a key securely to the disk
#           - Retrieves the key from storage
#           - Ability to generate keys and salts given a password

import nacl.secret
import nacl.utils
import nacl.pwhash
import nacl.public
from nacl.encoding import Base64Encoder
import base64


# Simple function to check if a input is ascii
def is_ascii(text):
    return all(ord(c) < 128 for c in text)


def store_uname(pubKey, privKey, filename, toStore):
    try:
        box = nacl.public.Box(privKey, pubKey)
    except TypeError as e:
        print("Error: In Box Creation")
        return 1

    encrypted = box.encrypt(bytes(toStore, 'ascii'))

    with open(filename, 'w') as f:
        encrypted_content = base64.b64encode(encrypted).decode("ascii")
        f.write(encrypted_content)

    return 0

def store_key(publick, privatek,  filename, password):

    with open(filename, 'w') as f:
        f.write(publick.encode(Base64Encoder).decode())
        f.write(privatek.encode(Base64Encoder).decode())



########################################################################################################################
# Function: get_key(password)
# Purpose: Given a password in string format, the function will read the previously made file decrypt it using the stored
#   salt.
# Notes: Find a better way to seperate read key and salt
# #####################################################################################################################

def get_key(pubkey, privkey, filename):

    with open('filename', 'r') as f:
        encrypted = f.read()

    salt = base64.b64decode(encrypted[1])
    encrypted = base64.b64decode(encrypted[0])

    key = kdf(nacl.secret.SecretBox.KEY_SIZE, password, salt)
    box = nacl.secret.SecretBox(key)
    decryptKey = box.decrypt(encrypted)

    return decryptKey


########################################################################################################################
# Function: arb_keygen(password)
# Purpose: Given a password in string format, the function will generate and return a key and salt for that password
# Notes: Used for testing purposes, although may be useful later
# #####################################################################################################################


def arb_keygen(password):
    # Generate the key:
    password = bytes(password.encode('ascii'))
    kdf = nacl.pwhash.argon2i.kdf
    salt_size = nacl.pwhash.argon2i.SALTBYTES
    salt = nacl.utils.random(salt_size)
    key = kdf(nacl.secret.SecretBox.KEY_SIZE, password, salt)
    return key, salt


########################################################################################################################
# Function: test_suite()
# Purpose: A test suite for this set of functions. Verifies that the key is the same after encryption and storage as it
#   is before
# Notes: None
# #####################################################################################################################

def test_suite():
    try:
        # Tests 1 and 2 test the is ascii function
        assert is_ascii("Hello World") == True
        print("Test 1 is_ascii - Pass")
        assert is_ascii("¢£	¥§") == False
        print("Test 2 is_ascii - Pass")

        # Test 3: Storing a arb key and retrieving it
        key, salt = arb_keygen('go_tigers')
        store_key(key, salt, 'key_store.txt')
        assert key == get_key('go_tigers')
        print("Test 3 Storage and Retrieval - Pass")

        # Test 4: Same process with different password
        key, salt = arb_keygen('password')
        store_key(key, salt, 'key_store')
        assert key == get_key('password')
        print("Test 4 Storage and Retrieval - Pass")

    except Exception as e:
        print(e)


def main():
    test_suite()


if __name__ == "__main__":
    main()