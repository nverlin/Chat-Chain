# Author: Joseph Soares
# file: chatChain_control.py
# purpose: contains main control loop for program
# invoke: python3 chatChain_control.py

#print('\033[H\033[J') #clear console

#imports
from chatChain_main import *
from tendermint import Tendermint
from time import sleep
from user_account import *
from store_and_sanitize import *
from sys import argv
from getpass import getpass

#globals
GREETING='Welcome to ChatChain'
ADDRESSBOOK={}
USER_KEYS=None
BLOCK=None
DEBUG=False
SKIP_CLEAR=False
RESERVED_WORD_LIST_ID='reserved.id'
ADDRESSBOOK_KEY_PREFIX='addressbook.'
RESERVED_ID_LIST=['account.','account@','addressbook@']+[ADDRESSBOOK_KEY_PREFIX]+[RESERVED_WORD_LIST_ID]

def line_number():
	#begin line_number
	fileName=inspect.getfile(inspect.currentframe()).split('/')[-1]
	lineNo=inspect.currentframe().f_back.f_lineno
	string='<%s>'%fileName+'<ln:%i>'%lineNo
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
			if DEBUG:print('**',validInts,line_number())
			continue
		break
	return userValue
	#end get_valid_int

def send_message():
	#begin send_message
	#check the status of the blockhain
	if not BLOCK.get_status():print('Blockchain not ready');return

	#get message information
	messageInfo=get_message_info(ADDRESSBOOK,RESERVED_ID_LIST) #return (<keys>, <conversation ID>, <message>)
	convoID=messageInfo[1]
	if DEBUG:print('**',messageInfo,line_number())

	#get message info ready and write to blockchain
	messageDataHexString=build_message_data(messageInfo,USER_KEYS) #concat and encrypt
	BLOCK.broadcast_tx_commit('%s=%s'%(convoID,messageDataHexString))#key=convoID value=messageDataHexString
	#endsend_message

def load_addressbook(userName):
	#begin load_addressbook
	global ADDRESSBOOK

	#get addressbook data from the blockchain
	userAddressbookKey=ADDRESSBOOK_KEY_PREFIX+userName
	addressbookData=BLOCK.get_message_blockchain(userAddressbookKey)

	#parse data *[uName1,pubKey1@uname2,pubKey2]*
	if DEBUG:print('**check deliniating chars',line_number())
	addressbookData=addressbookData.split('@')
	for datum in addressbookData:
		datum=datum.rstrip().split(',')
		#print('length:',len(datum[0]))

		# add entries to addressbook
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
	userData,userName=menu()
	if not DEBUG:print('\033[H\033[J') #clear login screen

	if DEBUG: print('**test code to delete',line_number())
	'''
	print('loading temp userFile',line_number())
	file=open('userFile','r')
	userData=file.readlines()
	file.close()
	'''
	USER_KEYS=get_user_keys(userData.rstrip()) #*(publKey,privKey)*

	#load the users addressbook
	print('!!**load_addressbook disabled**!!',line_number())
	# load_addressbook(userName)
	#end setup_user

def check_messages():
	#begin check_messages
	#check the status of the blockhain
	if not BLOCK.get_status():print('Blockchain not ready');return

	#get convoID from user
	while True:
		skip=False
		convoID=input('Conversation ID: ')
		if DEBUG:print('**need to sanitize',line_number())
		
		#test if reserved
		if convoID=='':continue
		for word in RESERVED_ID_LIST:
			if word in convoID:
				if DEBUG:print('**word:',word,'convoID:',convoID,line_number())
				print('Invalid Conversation ID, Please choose another')
				skip=True
				break
		if skip:skip=False;continue
		break

	#query blockchain
	messagesList=BLOCK.get_message_blockchain(convoID)
	# if DEBUG:print('**',messagesList,line_number())
	if DEBUG:print('**messages received:',len(messagesList),line_number())

	#decrypt and display messages
	for message in messagesList:
		print(decrypt_message(message,USER_KEYS,DEBUG))

	input('Press Enter To Continue: ')
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

def display_directory():
	#begin display_directory
	if DEBUG:print('**display_contacts under construction',line_number())
	#get directorydata from blockchain

	#parse and store directory data

	#display directory

	#de-allocate directory

	pass
	#end display_directory

def add_contact():
	#begin add_contact
	if DEBUG:print('**add_contact under construction',line_number())

	if DEBUG:print('**add from directory option',line_number())

	while True:
		if DEBUG:print('need to sanitize',line_number())
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
			print('**[%i] %s'%(x,splitPath[x]),line_number())

	if DEBUG:print('**contactName:',contactName,line_number())


	hexPubKey=file.readline().rstrip()
	pubKey=nacl.public.PublicKey(hexPubKey,encoder=nacl.encoding.HexEncoder)
	#if DEBUG:print('**',type(pubKey),line_number())
	ADDRESSBOOK[contactName]=pubKey
	file.close()
	#end add_contact

def remove_contact():
	#begin remove_contact
	if DEBUG:print('**remove_contact under construction',line_number())
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
	if DEBUG:print('**update_user_file under construction',line_number())
	'''
	username=input('Username: ')
	password=input('Password: ')

	store_user(password,username,USER_KEYS[1],ADDRESSBOOK)
	'''
	#end update_user_file

def save_changes():
	#begin save_changes
	while True:
		save=input('Save changes? [y/n]: ')
		if save.lower()=='y' or save.lower()=='yes':
			update_user_file()
			break
		elif save.lower()=='n' or save.lower()=='no':
			break
		else:
			save=None
	#end save_changes

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
		options=[]
		# choicesDict={1:'test'}
		print(' Edit contacts')
		print('\t1. Add Contact');validOptions.append(1);options.insert(1,add_contact)
		print('\t2. Remove Contact');validOptions.append(2);options.insert(2,remove_contact)

		print('\t0. Return To Main Menu');validOptions.append(0);options.insert(0,save_changes)

		#get user selection and validate
		choice=get_valid_int(validOptions,'\n Selection: ')

		if DEBUG:print('**remove after testing',line_number())
		'''
		while True:
			try:
				choice=int(input('\n Selection: '))
			except ValueError:
				print('Invalid Entry')
				continue
			if choice not in validOptions:print('Invalid Entry');continue
			break
		'''

		#call chosen function
		options[choice]()

		if DEBUG: print('**delete after testing',line_number())
		'''
		if choice==0:
			save_changes()
		elif choice==1:
			add_contact()
		elif choice==2:
			remove_contact()
		'''
	#end edit_contacts

def main_menu():
	#begin main_menu
	global ADDRESSBOOK, SKIP_CLEAR
	validOptions=[]
	while True:
		options=[]
		if not DEBUG and not SKIP_CLEAR:print('\033[H\033[J');SKIP_CLEAR=False
		print('\n\t1. Check Messages');validOptions.append(1);options.insert(1,check_messages)
		print('\t2. Send Message');validOptions.append(2);options.insert(2,send_message)
		print('\t3. Display Directory');validOptions.append(3);options.insert(3,display_directory)
		print('\t4. Edit Contacts');validOptions.append(4);options.insert(4,edit_contacts)

		print('\t0. Exit ChatChain\n');validOptions.append(0);options.insert(0,graceful_exit)

		#Get selection from user with validation
		choice=get_valid_int(validOptions,' Selection: ')

		if DEBUG:print('**delete after testing',line_number())
		'''
		while 1:
			try:
				choice=int(input(' Selection: '))
			except ValueError:
				print('Invalid Entry')
				continue

			if choice not in validOptions:print('Invalid Entry');continue
			break
		'''

		#call function by choice
		print('choice',choice,line_number())
		if DEBUG:
			for x in range(len(options)):
				print('[%i]'%x,options[x])
		options[choice]()

		if DEBUG:print('**delete after testing',line_number())
		
		'''
		if choice==0:			
			graceful_exit()
		elif choice==1:
			check_messages()
		elif choice==2:
			send_message()
		elif choice==3:
			display_directory()
			SKIP_CLEAR=True
		elif choice==4:
			edit_contacts()
		'''
	#end main_menu

def greet_user():
	#begin greet_user
	global GREETING #set var to global scope
	print('\n',GREETING)
	sleep(1)
	#end greet_user

def start_blockchain():
	#begin start_blockchain
	global BLOCK
	#create instance
	BLOCK=Tendermint()
	if not BLOCK.get_status():
		print(' Blockchain not up\n Exiting')
		graceful_exit()
	#end start_blockchain

def graceful_exit():
	#begin graceful_exit
	if DEBUG:print('**uncomment error handling in __main__',line_number())
	print('\n Thank you for using ChatChain\n')
	sleep(2)
	if not DEBUG:print('\033[H\033[J')
	exit()
	#end graceful_exit

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
	graceful_exit()
	#end main

if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		print('\nUser Shutdown')
		sleep(3)
		graceful_exit()
'''
	except:
		graceful_exit()
'''
