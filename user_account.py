# Nate Verlin
# ChatChain
# File: user_account.py.py
# Purpose: To handle a user's account and password

import os
import store_and_sanitize
import chatChain_main
import nacl.pwhash
import nacl.utils
import nacl.secret
from nacl.encoding import Base64Encoder
from getpass import getpass
from tendermint import Tendermint
import binascii
from chatChain_control import graceful_exit as g
from chatChain_control import get_directory 


PAD = "^"
DELIMIETER = "~"
LOGINCOUNT = 10


def authorizeFile(pk, uname):
    directory = get_dir_dict()
    
    correct_key = directory[uname]

    p = nacl.public.PrivateKey(pk)
    
    if correct_key == p.public_key:
        return 0
    else:
        return 1

    
def get_dir_dict():
    directoryDict={}
    t = Tendermint()
    #get directory entries from blockchain and make dictionary
    directoryList=t.get_message_blockchain('global.directory')
    for entry in directoryList:
        key,value=entry.decode().split(',')
        value=nacl.public.PublicKey(value,encoder=nacl.encoding.HexEncoder)
        directoryDict[key]=value

    #return dictionary of directory
    return directoryDict


def get_directory_menu():
    t = Tendermint()
    str_list = []
    for i in t.get_message_blockchain("global.directory"):
        str_list.append(i.decode().split(",")[0])
    return str_list
    

def save_user(username, password, address_book):

    publick, privatek = chatChain_main.generate_public_key_set()                     # inital private and public key gen

    address_book[username] = publick

    store_and_sanitize.store_user(password, username, privatek, address_book)




def build_address_list(text):
    address_list = []
    if text is None:
        return address_list
    else:
        split_text = text.decode().split('\n')
        address_list = split_text[:-1]
        return address_list


def create_new_account():
    while 1:
        username = input("Enter your desired username (max 20 characters): ")       #check for duplicate usernames
        

        if len(username) < 21:                                                      # username cannot be longer than 20 chars
            if username in get_directory_menu():
                print("This username is already being used- please try a different one")
            else:
                break
        else:
            print('Username is too long. Please enter another')

    while 1:
        password1 = getpass("Password(min 10 characters, max 20 characters): ")
        password2 = getpass("Confirm Password: ")

        if password1 == password2 and len(password1) < 21 and len(password1) > 9:
            break
        else:
            print("Passwords either do not match or parameters are not met")

    save_user(username, password1, {})

    


def login():
    user_list = []

    login_counter = 0

    while 1:
        flag = 0
        if login_counter < LOGINCOUNT:
            input_username = input("Username: ")
            input_password = getpass("Password: ")
            encrypted_text = b''
            print("Loading...")

            if input_username not in get_directory_menu():
                print("Account does not exist - try again")
            else:
                try:
                    with open(".key." + input_username, "r") as f:
                        encrypted_pk_list = f.read()
                except:
                    print("Missing user file")
                    continue
                
                try:
                    encrypted_pk = encrypted_pk_list[2:-1]
                except:
                    print("Corrupt user file - Exiting 1")
                    g()

                try:    
                    salt = binascii.unhexlify(encrypted_pk[144:])
                    
                    just_encrypted_pk = binascii.unhexlify(encrypted_pk[:144])
                                 
                    input_password = bytes(input_password.encode('ascii'))
                except:
                    print("Invalid user file - Exiting")
                    g()


                kdf = nacl.pwhash.argon2i.kdf
                ops = nacl.pwhash.argon2i.OPSLIMIT_SENSITIVE
                mem = nacl.pwhash.argon2i.MEMLIMIT_SENSITIVE

                key = kdf(nacl.secret.SecretBox.KEY_SIZE, input_password, salt, opslimit=ops, memlimit=mem)

                try:
                    box = nacl.secret.SecretBox(key)
                except TypeError as e:
                    print("Error: Key must be 32 bytes to be securely stored")
                    return 1

                try:
                    decrypted_text = box.decrypt(just_encrypted_pk)
                    flag = 1
                except:
                    print("Incorrect username or password. Try again")
                    login_counter += 1
                    continue

                try:
                    if authorizeFile(decrypted_text, input_username) == 1: #bad file
                        print("Corrupted user file - Exiting 2")
                        g()
                except:
                    raise 
                    print("Corrupted Key File - Exiting 3\n")
                    g()

                if flag == 1:
                    break
        else:
            print("Too many failed login attempts...Exiting Chat-Chain")
            return 1

    if flag == 1:
        print("Successful login")
       

    return decrypted_text, input_username


def menu(): #the menu for account management

    while 1:
        print("Login\n")
        choice = input("\t1. Create new account\n\t2. Login\n\t0. Exit\n\nSelection (Ctrl+C to return):")
        if choice == "1":
            try:
                create_new_account()
            except KeyboardInterrupt:
                print("\n")
                continue
        elif choice == "2":
            try:
                decrypted_text, username = login()
            except KeyboardInterrupt:
                print("\n")
                continue
            break
        elif choice == "0":
            g()
        else:
            print("Please enter a valid option")

    return decrypted_text, username


def main():
    menu()


if __name__ == "__main__":
    main()

