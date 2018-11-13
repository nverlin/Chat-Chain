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
import base64


# Simple function to check if a input is ascii
def is_ascii(text):
    return all(ord(c) < 128 for c in text)

########################################################################################################################
# Function: store_key(key, salt)
# Purpose: Given a key to store and the associated salt, the function will encrypt they key and store it to a file along
#   with the salt in base64 encoding
# Notes: Need to find a better way to combine then seperate the input and the salt...currently using a delimiter ' '
# ######################################################################################################################

def store_key(key, salt):
    try:
        box = nacl.secret.SecretBox(key)
    except TypeError as e:
        print("Error: Key must be 32 bytes to be securely stored")
        return 1

    encrypted = box.encrypt(key)

    with open('key_store.txt', 'w') as f:
        encrypted_content = base64.b64encode(encrypted).decode("ascii")
        encrypted_salt = base64.b64encode(salt).decode("ascii")
        f.write(encrypted_content)
        f.write(' ')
        f.write(encrypted_salt)
    return 0

########################################################################################################################
# Function: get_key(password)
# Purpose: Given a password in string format, the function will read the previously made file decrypt it using the stored
#   salt.
# Notes: Find a better way to seperate read key and salt
# #####################################################################################################################

def get_key(password):
    password = bytes(password.encode('ascii'))
    kdf = nacl.pwhash.argon2i.kdf

    with open('key_store.txt', 'r') as f:
        encrypted = f.read().split(' ')

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
        store_key(key, salt)
        assert key == get_key('go_tigers')
        print("Test 3 Storage and Retrieval - Pass")

        # Test 4: Same process with different password
        key, salt = arb_keygen('password')
        store_key(key, salt)
        assert key == get_key('password')
        print("Test 4 Storage and Retrieval - Pass")

    except Exception as e:
        print(e)


def main():
    test_suite()


if __name__ == "__main__":
    main()