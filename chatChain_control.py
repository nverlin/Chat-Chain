# Author: Joseph Soares
# file: chatChain_control.py
# purpose: contains main control loop for program
# invoke: python3 chatChain_control.py

#print('\033[H\033[J') #clear console

#imports
from chatChain_main import *
from tendermint import Tendermint
import time
from user_account import *
from store_and_sanitize import *
from sys import argv

#globals
GREETING='Welcome to ChatChain'
ADDRESSBOOK={}
USER_KEYS=None
BLOCK=None
DEBUG=False

def line_number():
	#begin line_number
	string='<%s>'%sys.argv[0]+'<ln:%i>'%inspect.currentframe().f_back.f_lineno
	return string
	#end line_number

def get_valid_int(validInts,prompt):
	#begin get_valid_int
	while True:
		userValue=input(prompt)
		try:
			userValue=int(userValue)
		except ValueError:
			print('Invalid Entry')
			continue
		if userValue not in validInts:
			print('Invalid Entry')
			if DEBUG:print(validInts)
			continue
		break
	return userValue
	#end get_valid_int

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

	#print(len(addressbookData),addressbookData,line_number())

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
	if not DEBUG:print('\033[H\033[J') #clear login screen

	'''
	print('loading temp userFile',line_number())
	file=open('userFile','r')
	userData=file.readlines()
	file.close()
	'''
	USER_KEYS=get_user_keys(userData[0].rstrip()) #*(publKey,privKey)*

	#print(len(userData),userData,line_number())

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

	while True:
		choice=input('Finished? [y/n]: ')
		choice=choice.lower()
		if choice=='yes' or choice=='y':
			break
	#end check_messages

def display_contacts(addressbook):
	#begin display_contacts
	#display contents of addressbook to std out
	count=1
	print('\n Contacts')
	for user in addressbook:
		print('\t%i. %s'%(count,user))
		count+=1
	print('')
	#end display_contacts

def add_contact():
	#begin add_contact
	#print('add_contact under construction',line_number())
	while True:
		print('need to sanitize',line_number())
		filePath=input('Path to contact card: ')
		#filePath='/home/chain/Desktop/bob.card'
		try:
			file=open(filePath,'r')
		except IOError:
			print('Bad file path')
			continue
		break
	splitPath=filePath.split('/')

	contactName=splitPath[-1][:-5]

	if DEBUG:
		for x in range(len(splitPath)):
			print('[%i] %s'%(x,splitPath[x]))

	if DEBUG:print('contactName:',contactName)


	hexPubKey=file.readline().rstrip()
	pubKey=nacl.public.PublicKey(hexPubKey,encoder=nacl.encoding.HexEncoder)
	#if DEBUG:print(type(pubKey),line_number())
	ADDRESSBOOK[contactName]=pubKey
	file.close()
	#end add_contact

def remove_contact():
	#begin remove_contact
	print('remove_contact under construction',line_number())
	global ADDRESSBOOK
	validDict={}
	index=1
	for key in ADDRESSBOOK:
		validDict[index]=key
		index+=1
	choice=get_valid_int([*validDict.keys()],'Selection: ')

	ADDRESSBOOK.pop(validDict[choice])
	#end remove_contact

def update_user_file():
	#begn update_user_file
	print('update_user_file under construction')
	pass
	#end update_user_file

def edit_contacts():
	#begin edit_contacts
	print('edit_contacts under construction',line_number())

	while True:
		if not DEBUG:print('\033[H\033[J')
		global ADDRESSBOOK
		#display contacts
		display_contacts(ADDRESSBOOK)

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
				choice=int(input('\n Selection: '))
			except ValueError:
				print('Invalid Entry')
				continue
			if choice not in validOptions:print('Invalid Entry');continue
			break

		#call chosen function
		if choice==0:
			while True:
				save=input('Save changes? [y/n]: ')
				if save.lower()=='y' or save.lower()=='yes':
					update_user_file()
					break
				elif save.lower()=='n' or save.lower()=='no':
					break
				else:
					save=None
			return
		elif choice==1:
			add_contact()
		elif choice==2:
			remove_contact()
	#end edit_contacts

def main_menu():
	#begin main_menu
	global ADDRESSBOOK
	validOptions=[]
	while True:
		if not DEBUG:print('\033[H\033[J')
		if not DEBUG:print('screen cleat blows out message print')
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
			graceful_exit()
		elif choice==1:
			check_messages()
		elif choice==2:
			send_message()
		elif choice==3:
			display_contacts(ADDRESSBOOK)
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
	#end start_blockchain

def main():
	#begin main
	global DEBUG
	if len(argv)==2:
		if argv[1].lower()=='debug': DEBUG=True
	if not DEBUG:print('\033[H\033[J')
	'''!!!!!SHOULD ONLY CONTAIN FUNCTION CALLS!!!!!'''
	start_blockchain()
	setup_user()
	greet_user()
	main_menu()
	pass
	#end main

def graceful_exit():
	#begin graceful_exit
	print('uncomment error handling',line_number())
	exit()
	#end graceful_exit

if __name__ == '__main__':
	main()
	graceful_exit()
	'''
	try:
		main()
	except:
		print('implement graceful shutdown')
	'''