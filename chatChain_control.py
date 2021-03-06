# Author: Joseph Soares
# file: chatChain_control.py
# purpose: contains main control loop for program
# invoke: python3 chatChain_control.py [<debug>]

#print('\033[H\033[J') #clear console

#imports
from chatChain_main import *
from tendermint import Tendermint
from time import sleep
from user_account import *
from store_and_sanitize import *
from sys import argv
from getpass import getpass
from os.path import expanduser

#globals
GREETING='Welcome to ChatChain'
ADDRESSBOOK={}
USER_NAME=None
USER_KEYS=None #*(publKey,privKey)*
BLOCK=None
DEBUG=False
SKIP_CLEAR=False

#reserved words
RESERVED_WORD_LIST_ID='reserved.id'
ADDRESSBOOK_KEY_PREFIX='addressbook.'
DIRECTORY_KEY='global.directory'
DIRECTORY_IGNORE_KEY_PREFIX='ignore.'
USER_ACCOUNT_KEY_PREFIX='account.'
USER_PASSWORD_KEY_PREFIX='password.'
RESERVED_ID_LIST=[USER_ACCOUNT_KEY_PREFIX]+[USER_PASSWORD_KEY_PREFIX]+[ADDRESSBOOK_KEY_PREFIX]+[DIRECTORY_KEY]+[DIRECTORY_IGNORE_KEY_PREFIX]+[RESERVED_WORD_LIST_ID]

def line_number():
	#begin line_number
	fileName=inspect.getfile(inspect.currentframe()).split('/')[-1]
	lineNo=inspect.currentframe().f_back.f_lineno
	string='<%s>'%fileName+'<ln:%i>'%lineNo
	return string
	#end line_number

def do_nothing():
	#begin do_nothing
	#placeholder function that does nothing
	pass
	#end do_nothing

def get_valid_int(validInts,prompt):
	#begin get_valid_int
	#get calid int from user
	while True:
		userValue=input(prompt)
		try:
			userValue=int(userValue)
		except ValueError:
			print(' *Invalid Entry')
			continue
		if userValue not in validInts:
			print(' *Invalid Entry')
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
	messageInfo=get_message_info(ADDRESSBOOK,RESERVED_ID_LIST,DEBUG) #return (<keys>, <conversation ID>, <message>)
	convoID=messageInfo[1]
	if DEBUG:print('**',messageInfo,line_number())

	#get message info ready and write to blockchain
	messageDataHexString=build_message_data(messageInfo,USER_KEYS,USER_NAME,DEBUG) #concat and encrypt
	BLOCK.broadcast_tx_commit('%s=%s'%(convoID,messageDataHexString))#key=convoID value=messageDataHexString
	print(' Message sent')
	sleep(2)
	#endsend_message

def load_addressbook(userName):
	#begin load_addressbook
	global ADDRESSBOOK #set var to global scope

	if DEBUG:print(userName);print(USER_NAME)

	#get addressbook data from the blockchain
	userAddressbookKey=ADDRESSBOOK_KEY_PREFIX+userName
	addressbookData=BLOCK.get_message_blockchain(userAddressbookKey)

	if DEBUG:print('addressbook:', len(addressbookData),line_number())

	#keep newest copy of addressbook
	addressbookData=addressbookData[-1].decode()

	#parse entries from data *[uName1,pubKey1@uname2,pubKey2]*
	if DEBUG:print('**check deliniating chars',line_number())
	addressbookData=addressbookData.split('@')
	for datum in addressbookData:
		datum=datum.rstrip().split(',')

		if DEBUG:print(datum,line_number())

		# add entries to addressbook
		ADDRESSBOOK[datum[0]]=nacl.public.PublicKey(datum[1],encoder=nacl.encoding.HexEncoder)
	#end load_addressbook

def get_user_keys(keyString):
	#begin get_user_keys
	#get type key from string
	keySet=nacl.public.PrivateKey(keyString)
	return (keySet.public_key,keySet)
	#end get_user_keys

def setup_user():
	#begin setup_user
	global USER_KEYS,USER_NAME #set vars to global scope

	#authenticate user func from Nathan, should return (keyBin,uname)
	keyBin,userName=menu()

	if not DEBUG:print('\033[H\033[J') #clear login screen

	#set username and keys
	USER_NAME=userName
	USER_KEYS=get_user_keys(keyBin) #*(publKey,privKey)*

	#load the users addressbook
	load_addressbook(userName)
	#end setup_user

def check_messages():
	#begin check_messages
	#check the status of the blockhain
	if not BLOCK.get_status():print('Blockchain not ready');return

	#get convoID from user
	while True:
		skip=False
		convoID=input('\n Conversation ID: ')

		#test if reserved
		if convoID=='':continue
		for word in RESERVED_ID_LIST:
			if word in convoID:
				if DEBUG:print('**word:',word,'convoID:',convoID,line_number())
				print(' *Invalid Conversation ID, Please choose another')
				skip=True
				break
		if skip:skip=False;continue
		break

	#query blockchain
	messagesList=BLOCK.get_message_blockchain(convoID)

	if DEBUG:print('**messages received:',len(messagesList),line_number())

	#decrypt and display messages
	print('\033[H\033[J') #clear console
	print('Conversation: %s\n'%convoID)
	for message in messagesList:
		plainMessage=decrypt_message(message,USER_KEYS,DEBUG)
		if not plainMessage=='':
			print(plainMessage)

	#pause to let user read messages
	input('\n Enter To Return: ')
	#end check_messages

def display_contacts(hold=True):
	#begin display_contacts	
	global ADDRESSBOOK
	#print contents of addressbook to std out
	count=1
	print('\n Contacts\n')
	for user in ADDRESSBOOK:
		print('\t%i. %s'%(count,user))
		count+=1
	print('')
	if hold:input('\n Enter To Return:')
	#end display_contacts

def get_directory():
	#begin get_directory
	directoryDict={}

	#get directory entries from blockchain and make dictionary
	directoryList=BLOCK.get_message_blockchain(DIRECTORY_KEY)
	for entry in directoryList:
		key,value=entry.decode().split(',')
		value=nacl.public.PublicKey(value,encoder=nacl.encoding.HexEncoder)
		directoryDict[key]=value

	#return dictionary of directory
	return directoryDict
	#end get_directory

def display_directory():
	#begin display_directory
	if DEBUG:print('**display_contacts under construction',line_number())
	#get directorydata from blockchain
	directory=get_directory()

	#display directory
	count=1
	print(' Directory')
	for entry in directory:
		print('\t%i. %s'%(count,entry))
		count+=1

	#de-allocate directory
	directory=None

	input('\n Enter To Return:')
	#end display_directory

def add_contact_from_card():
	#begin add_contact_from_card
	#get path to card from user
	while True:
		filePath=input('\n Path to contact card: ')

		#open contact card
		try:
			file=open(filePath,'r')
		except IOError:
			print('Bad file path')
			continue
		break

	#get contact user name
	splitPath=filePath.split('/')
	contactName=splitPath[-1][:-5]
	if DEBUG:print('**contactName:',contactName,line_number())

	#get key from card file
	hexPubKey=file.readline().rstrip()
	file.close()
	pubKey=nacl.public.PublicKey(hexPubKey,encoder=nacl.encoding.HexEncoder)

	#add to addressbook
	ADDRESSBOOK[contactName]=pubKey
	#end add_contact_from_card

def add_contact_from_directory():
	#begin add_contact_from_directory
	#get directory
	directory=get_directory()

	#display directory and build optionsList
	optionsDict={}
	validOptions=[0]
	choice=9999
	count=1
	print('\n Directory\n')
	for entry in directory:
		print('\t%i. %s'%(count,entry))
		validOptions+=[count]
		optionsDict[count]=entry
		count+=1

	# get user selection and add entry
	print('')
	while True:
		choice=get_valid_int(validOptions,' selection (0 to return): ')
		if choice==0:
			break
		ADDRESSBOOK[optionsDict[choice]]=directory[optionsDict[choice]]
	#end add_contact_from_directory

def add_contact():
	#begin add_contact
	if DEBUG:print('**add_contact under construction',line_number())
	if DEBUG:print('**add from directory option',line_number())

	options=[]
	validOptions=[]

	#print add_contact menu and build options list
	if not DEBUG:print('\033[H\033[J')
	print(' Contact Source\n')
	print('\t1. Directory');validOptions.append(1);options.insert(1,add_contact_from_directory)
	print('\t2. Contact Card');validOptions.append(2);options.insert(2,add_contact_from_card)
	print('\t0. Return To Previous Menu\n');validOptions.append(0);options.insert(0,do_nothing)

	#get user selection
	choice=get_valid_int(validOptions,'\n Selection: ')

	#choose option
	options[choice]()

	return False
	#end add_contact

def remove_contact():
	#begin remove_contact
	global ADDRESSBOOK
	if DEBUG:print('**remove_contact under construction',line_number())
	
	#buil dictionary of valid options and usernames
	validDict={}
	index=1
	for key in ADDRESSBOOK:
		validDict[index]=key
		index+=1

	#get choice from user
	choice=get_valid_int([*validDict.keys()],'\n Selection: ')

	#remove the user's choice
	ADDRESSBOOK.pop(validDict[choice])
	return False
	#end remove_contact

def update_addressbook():
	#begn update_addressbook
	global USER_NAME
	addressbookList=[]

	#build string of addressbook to commit to blockchain
	for userName,pubKey in zip(ADDRESSBOOK.keys(),ADDRESSBOOK.values()):
		addressbookList.append(userName+','+pubKey.encode(encoder=nacl.encoding.HexEncoder).decode())
	addressbookString=ADDRESSBOOK_KEY_PREFIX+USER_NAME+'='+'@'.join(addressbookList)

	if DEBUG:print(addressbookString) #debug

	#write to blockchain
	BLOCK.broadcast_tx_commit(addressbookString)	
	#end update_addressbook

def create_contact_card():
	#begin create_contact_card
	global USER_NAME
	if DEBUG:print('**prints to working directory, need to make desktop, relative',line_number()) #debug

	#get filename and path to desktop
	fileName=expanduser('~/Desktop/')+'%s.card'%USER_NAME

	#open contact card
	try:
		file=open(fileName,'w')
	except IOError:
		print(' Unable to create file %s,\n Contact Card Not Created\n'%fileName)
		return

	#generate hexstring from public key
	hexOfPubKey=USER_KEYS[0].encode(encoder=nacl.encoding.HexEncoder).decode()
	if DEBUG:print('key=%s'%hexOfPubKey)

	#write to file
	file.write(hexOfPubKey)
	file.close()

	#report success to user
	print('\n Contact card saved to desktop')
	sleep(2)
	#end create_contact_card

def save_changes():
	#begin save_changes
	#promt user if they want to save changes to addressbook
	while True:
		save=input('\n Save changes? [y/n]: ')
		if save.lower()=='y' or save.lower()=='yes':
			update_addressbook()
			break
		elif save.lower()=='n' or save.lower()=='no':
			break
		else:
			save=None
	return True
	#end save_changes

def edit_contacts():
	#begin edit_contacts
	print('edit_contacts under construction',line_number())

	while True:
		if not DEBUG:print('\033[H\033[J')
		global ADDRESSBOOK

		#print contacts to std out
		display_contacts(False)

		#display edit contacts menu and build list of options
		validOptions=[]
		options=[]
		print(' Edit contacts\n')
		print('\t1. Add Contact');validOptions.append(1);options.insert(1,add_contact)
		print('\t2. Remove Contact');validOptions.append(2);options.insert(2,remove_contact)
		print('\t3. Create Contact Card');validOptions.append(3);options.insert(3,create_contact_card)

		print('\t0. Return To Main Menu');validOptions.append(0);options.insert(0,save_changes)

		#get user selection and validate
		choice=get_valid_int(validOptions,'\n Selection: ')

		#call chosen function
		if options[choice]():break
	#end edit_contacts

def main_menu():
	#begin main_menu
	global ADDRESSBOOK, SKIP_CLEAR
	validOptions=[]
	while True:
		options=[]
		#print main menu and build list of options
		if not DEBUG and not SKIP_CLEAR:print('\033[H\033[J');SKIP_CLEAR=False
		if SKIP_CLEAR:SKIP_CLEAR=False
		print(' Main Menu\n')
		print('\t1. Check Messages');validOptions.append(1);options.insert(1,check_messages)
		print('\t2. Send Message');validOptions.append(2);options.insert(2,send_message)
		print('\t3. Display Directory');validOptions.append(3);options.insert(3,display_directory)
		print('\t4. Display Addressbook'),validOptions.append(4);options.insert(4,display_contacts)
		print('\t5. Edit Contacts');validOptions.append(5);options.insert(5,edit_contacts)

		print('\t0. Exit ChatChain\n');validOptions.append(0);options.insert(0,graceful_exit)

		#Get selection from user with validation
		choice=get_valid_int(validOptions,' Selection: ')

		#call function by choice
		if  DEBUG:print('choice',choice,line_number())
		if DEBUG:
			for x in range(len(options)):
				print('[%i]'%x,options[x])
		options[choice]()
	#end main_menu

def greet_user():
	#begin greet_user
	global GREETING,SKIP_CLEAR #set var to global scope
	print(' '+GREETING,'\n')
	SKIP_CLEAR=True
	#sleep(1)
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
	global DEBUG #set var to global scope

	#check for debug mode
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
	except:
		graceful_exit()
