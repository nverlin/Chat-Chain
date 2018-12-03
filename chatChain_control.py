# Author: Joseph Soares
# file: chatChain_control.py
# purpose: contains main control loop for program
# invoke: python3 chatChain_control.py

#imports
from chatChain_main import *
from tendermint import Tendermint
import time
from user_account import *
from store_and_sanitize import *

#globals
GREETING='Welcome to ChatChain'
ADDRESSBOOK={}
USER_KEYS=None
BLOCK=None

def line_number():
	#begin line_number
	string='<%s>'%sys.argv[0]+'<ln:%i>'%inspect.currentframe().f_back.f_lineno
	return string
	#end line_number

def send_message():
	#begin send_message
	messageInfo=get_message_info(ADDRESSBOOK) #return (<keys>, <conversation ID>, <message>)
	convoID=messageInfo[1]
	print(messageInfo,line_number())
	messageDataHexString=build_message_data(messageInfo,USER_KEYS)
	BLOCK.broadcast_tx_commit('%s=%s'%(convoID,messageDataHexString))

	#delete after
	testhexstring1=''
	
	file=open('test','r')
	testhexstring2=file.readline().rstrip()
	file.close()
	print(testhexstring1==testhexstring2,line_number())
	#endsend_message

def load_addressbook(addressbookData):
	#begin load_addressbook
	global ADDRESSBOOK	

	print(len(addressbookData),addressbookData)

	for datum in addressbookData:
		datum=datum.rstrip().split(',')
		print('length:',len(datum[0]))

		ADDRESSBOOK[datum[1]]=nacl.public.PublicKey(datum[0],encoder=nacl.encoding.HexEncoder)
	#end load_addressbook

def get_user_keys(keyString):
	#begin get_user_keys
	keySet=nacl.public.PrivateKey(keyString,encoder=nacl.encoding.HexEncoder)
	return (keySet.public_key,keySet)
	#end get_user_keys

def setup_user():
	#begin setup_user
	global USER_KEYS

	#authenticate user func from Nathan, should return contents of user file
	userData=menu()
	'''
	print('loading temp userFile',line_number())
	file=open('userFile','r')
	userData=file.readlines()
	file.close()
	'''
	USER_KEYS=get_user_keys(userData[0].rstrip()) #*(publKey,privKey)*

	print(len(userData),userData,line_number())

	load_addressbook(userData[1:])
	#end setup_user

def check_messages():
	#begin check_messages
	#get convoID from user
	convoID=input('Conversation ID: ')
	print('need to sanitize',line_number())

	#query blockchain
	messagesList=BLOCK.get_message_blockchain(convoID)

	print('***for tessting only***',line_number())
	messagesList=messagesList[1:]

	#decrypt and display messages
	for message in messagesList:
		print(decrypt_message(message,USER_KEYS))
	#end check_messages

def display_contacts():
	#begin display_contacts
	global ADDRESSBOOK
	print('display_contacts under construction',line_number())
	#display contents of addressbook to std out

	count=1
	for user in ADDRESSBOOK:
		print('%i. %s'%(count,user))

	#end display_contacts

def edit_contacts():
	#begin edit_contacts
	print('edit_contacts under construction',line_number())
	#display contacts
	display_contacts()

	#display edit contacts menu
	validOptions=[]
	choicesDict={1:'test'}
	print(' Edit contacts')
	print('\t1. Add Contact');validOptions.append(1)
	print('\t2. Remove Contact');validOptions.append(2)


	print('\t0. Return To Main Menu');validOptions.append(0)

	#get user selection and validate
	while True:
		try:
			choice=int(input(' Selection: '))
		except ValueError:
			print('Invalid Entry')
			continue
		if choice not in validOptions:print('Invalid Entry');continue
		break

	#call chosen function
	if choice==0:
		return
	else:
		pass
	pass
	#end edit_contacts

def main_menu():
	#begin main_menu
	validOptions=[]
	while True:
		print('\n\t1. Check Messages');validOptions.append(1)
		print('\t2. Send Message');validOptions.append(2)
		print('\t3. Display Contacts');validOptions.append(3)
		print('\t4. Edit Contacts');validOptions.append(4)

		print('\t0. Exit ChatChain\n');validOptions.append(0)

		#Get selection from user with validation
		while 1:
			try:
				choice=int(input(' Selection: '))
			except ValueError:
				print('Invalid Entry')
				continue

			if choice not in validOptions:print('Invalid Entry');continue
			break
		
		if choice==0:
			print('\n Thank you for using ChatChain\n')
			time.sleep(2)
			exit()
		elif choice==1:
			check_messages()
		elif choice==2:
			send_message()
		elif choice==3:
			display_contacts()
		elif choice==4:
			edit_contacts()

	#end main_menu

def greet_user():
	#begin greet_user
	global GREETING #set var to global scope
	print('\n',GREETING,'\n')
	time.sleep(1)
	pass
	#end greet_user

def start_blockchain():
	#begin start_blockchain
	global BLOCK
	#initialize and sync blockchain instance
	#create instance
	BLOCK=Tendermint()
	pass
	#end start_blockchain

def main():
	#begin main
	'''!!!!!SHOULD ONLY CONTAIN FUNCTION CALLS!!!!!'''
	start_blockchain()
	setup_user()
	greet_user()
	main_menu()
	pass
	#end main

if __name__ == '__main__':
	main()