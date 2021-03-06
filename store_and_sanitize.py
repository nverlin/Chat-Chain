# Nate Verlin
# ChatChain
# File: store_and_sanitize.py
# This file contains the store user function that is responsible for storing the user to both the disk and the blockchain

import nacl.secret
import nacl.utils
import nacl.pwhash
import nacl.public
import nacl.encoding
from tendermint import Tendermint
import binascii
import os



def store_user(password, username, privateKey, address_book): # kdfs the private key, saves it, adds user to directory on block chain, creates address book, greets user
    print("Creating...")
    password = bytes(password.encode('ascii'))
    kdf = nacl.pwhash.argon2i.kdf
    salt_size = nacl.pwhash.argon2i.SALTBYTES
    salt = nacl.utils.random(salt_size)
    ops = nacl.pwhash.argon2i.OPSLIMIT_SENSITIVE
    mem = nacl.pwhash.argon2i.MEMLIMIT_SENSITIVE

    key = kdf(nacl.secret.SecretBox.KEY_SIZE, password, salt, opslimit=ops, memlimit=mem)

    try:
        box = nacl.secret.SecretBox(key)
    except TypeError as e:
        print("Error: Key must be 32 bytes to be securely stored")
        return 1


    encrypted_password = box.encrypt(password)
    
    encrypted_pk = box.encrypt(bytes(privateKey))


    key = "addressbook." + username 
    value = '=' + username + ',' + privateKey.public_key.encode(encoder=nacl.encoding.HexEncoder).decode()
    

    t = Tendermint()
    t.broadcast_tx_commit("global.directory=" + username + ','  + privateKey.public_key.encode(encoder=nacl.encoding.HexEncoder).decode()) #all usernames
    t.broadcast_tx_commit(key + value)
    

    with open(".key." + username, 'w+') as f:
        f.write(str(binascii.hexlify(encrypted_pk) + binascii.hexlify(salt)))
    os.chmod(".key." + username, 0o400) 

    print('\033[H\033[J')    
    print("\nWelcome to ChatChain " + username)

def main():
    test_suite()


if __name__ == "__main__":
    main()