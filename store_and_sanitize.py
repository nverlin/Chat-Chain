# Nate Verlin
# ChatChain
# File: store_and_sanitize.py
# This file is designed to provide some basic utility functions for the chat chain program.

import nacl.secret
import nacl.utils
import nacl.pwhash
import nacl.public



# Simple function to check if a input is ascii
def is_ascii(text):
    return all(ord(c) < 128 for c in text)


def store_user(password, username, privateKey, address_book): # this can be called a needed to update user
    password = bytes(password.encode('ascii'))
    kdf = nacl.pwhash.argon2i.kdf
    salt_size = nacl.pwhash.argon2i.SALTBYTES
    salt = nacl.utils.random(salt_size)
    key = kdf(nacl.secret.SecretBox.KEY_SIZE, password, salt)

    try:
        box = nacl.secret.SecretBox(key)
    except TypeError as e:
        print("Error: Key must be 32 bytes to be securely stored")
        return 1

    concat_address_book = ''
    for key, value in address_book.items():
        concat_address_book += value.decode() + ',' + key + '\n'
    encrypted = box.encrypt(bytes(privateKey) + bytes(concat_address_book.encode()))

    with open(username, 'wb') as f:
        f.write(salt + b'\n') # write salt then private key
        f.write(encrypted)




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
        print("Removed Test Suite")

    except Exception as e:
        print(e)


def main():
    test_suite()


if __name__ == "__main__":
    main()