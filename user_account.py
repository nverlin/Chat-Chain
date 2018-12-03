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

PAD = "^"
DELIMIETER = "~"
LOGINCOUNT = 12


def save_user(username, password, address_book):

    publick, privatek = chatChain_main.generate_public_key_set()  # inital private and public key gen

    address_book[username] = publick

    store_and_sanitize.store_user(password, username, privatek, address_book)

    print("Business Card(saved on desktop)\nUsername:", username, "\nPublic Key: ", publick.encode(nacl.encoding.HexEncoder).decode())

    desktop = os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop')

    with open(desktop + '/' + username + '.card', 'w') as f:
        f.write(publick.encode(nacl.encoding.HexEncoder).decode())
        f.write('\n')


def build_address_list(text):
    address_list = []
    # print(text)
    if text is None:
        return address_list
    else:
        split_text = text.decode().split('\n')
        # print(split_text[:-1])
        address_list = split_text[:-1]
        return address_list


def create_new_account():
    while 1:
        username = input("Enter your desired username (max 20 characters): ") #check for duplicate usernames

        choice = input("Username is " + username + "\nConfirm (y/n):")
        if (choice == 'y' or choice == 'Y') and len(username) < 21:
            break

    while 1:
        password1 = input("Password(min 10 characters, max 20 characters): ")
        password2 = input("Confirm Password: ")

        if password1 == password2 and len(password1) < 21:
            break
        else:
            print("Passwords did not match please try again")

    save_user(username, password1, {})


def login():
    user_list = []

    login_counter = 0

    while 1:
        if login_counter < LOGINCOUNT:
            input_username = input("Username: ")
            input_password = input("Password: ")
            encrypted_text = b''

            try:
                with open(input_username, 'rb') as f:
                    encrypted_text = f.readlines()

            except:
                print("Invalid user name or password")
                login_counter +=1
                continue

            salt = encrypted_text[0]
            salt = salt[:-1]

            cipher = encrypted_text[1]

            input_password = bytes(input_password.encode('ascii'))

            kdf = nacl.pwhash.argon2i.kdf

            key = kdf(nacl.secret.SecretBox.KEY_SIZE, input_password, salt)

            try:
                box = nacl.secret.SecretBox(key)
            except TypeError as e:
                print("Error: Key must be 32 bytes to be securely stored")
                return 1

            try:
                decrypted_text = box.decrypt(cipher)
            except:
                print("Incorrect username or password. Try again")
                login_counter += 1
            break
        else:
            print("Too many failed login attempts...Exiting Chat-Chain")
            return 1

    privateKey = decrypted_text[:32]
    
    user_list.append(privateKey.hex())

    address_book_list = build_address_list(decrypted_text[32:])

    for i in address_book_list:
        user_list.append(i)

    return user_list # this final list is in format ['dcfbdec6f5082805ef5b2f37689826291a2c431ed29838bd271f592ae7cbb513', '40bf496f0945cc1eaf11e00d11cefa434585ed181e8645046eaa8fc75030fc5,joe', etc]


def menu():

    while 1:
        print("Account Creation - Please enter the number of your desired option")
        choice = input("1. Create new account\n2. Login\n:")
        if choice == "1":
            create_new_account()
        elif choice == "2":
            user_list = login()
            break
        else:
            print("Please enter a valid option")

    return user_list


def main():
    menu()


if __name__ == "__main__":
    main()

