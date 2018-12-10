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

	if DEBUG:print(userName);print(USER_NAME)
	#get addressbook data from the blockchain
	userAddressbookKey=ADDRESSBOOK_KEY_PREFIX+userName
	addressbookData=BLOCK.get_message_blockchain(userAddressbookKey)

	if DEBUG:print('addressbook:', len(addressbookData),addressbookData,line_number())

	addressbookData=addressbookData[-1].decode()

	if DEBUG:print(addressbookData,line_number())

	#parse data *[uName1,pubKey1@uname2,pubKey2]*
	if DEBUG:print('**check deliniating chars',line_number())
	addressbookData=addressbookData.split('@')
	for datum in addressbookData:
		datum=datum.rstrip().split(',')

		if DEBUG:print(datum,line_number())

		if DEBUG:print(datum[1],len(datum[1]),line_number())

		# add entries to addressbook
		ADDRESSBOOK[datum[0]]=nacl.public.PublicKey(datum[1],encoder=nacl.encoding.HexEncoder)
	#end load_addressbook

def get_user_keys(keyString):
	#begin get_user_keys
	keySet=nacl.public.PrivateKey(keyString)
	return (keySet.public_key,keySet)
	#end get_user_keys

def setup_user():
	#begin setup_user
	global USER_KEYS

	#authenticate user func from Nathan, should return (keyBin,uname)
	keyBin,userName=menu()

	if not DEBUG:print('\033[H\033[J') #clear login screen

	if DEBUG: print('**test code to delete',line_number())
	'''
	print('loading temp userFile',line_number())
	file=open('userFile','r')
	userData=file.readlines()
	file.close()
	'''
	USER_NAME=userName
	USER_KEYS=get_user_keys(keyBin) #*(publKey,privKey)*

	#load the users addressbook
	# print('!!**load_addressbook disabled**!!',line_number())
	load_addressbook(userName)
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
		plainMessage=decrypt_message(message,USER_KEYS,DEBUG)
		if not plainMessage=='':
			print(plainMessage)

	input('Press Enter To Continue: ')
	#end check_messages

def display_contacts():
	#begin display_contacts	
	global ADDRESSBOOK
	#display contents of addressbook to std out
	count=1
	print('\n Contacts')
	for user in ADDRESSBOOK:
		print('\t%i. %s'%(count,user))
		count+=1
	print('')
	#end display_contacts

def get_directory():
	#begin get_directory
	directoryDict={}
	directoryList=BLOCK.get_message_blockchain(DIRECTORY_KEY)
	for entry in directoryList:
		key,value=entry.decode().split(',')
		value=nacl.public.PublicKey(value,encoder=nacl.encoding.HexEncoder)
		directoryDict[key]=value

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
	#end display_directory

def add_contact_from_card():
	#begin add_contact_from_card
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

	# if DEBUG:
	# 	for x in range(len(splitPath)):
	# 		print('**[%i] %s'%(x,splitPath[x]),line_number())

	if DEBUG:print('**contactName:',contactName,line_number())

	hexPubKey=file.readline().rstrip()
	file.close()

	pubKey=nacl.public.PublicKey(hexPubKey,encoder=nacl.encoding.HexEncoder)
	#if DEBUG:print('**',type(pubKey),line_number())
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
	print(' Directory')
	for entry in directory:
		print('\t%i. %s'%(count,entry))
		validOptions+=[count]
		optionsDict[count]=entry
		count+=1

	# get user selection and add entry
	while True:
		choice=get_valid_int(validOptions,' selection (0 to exit): ')
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

	#print add_contact menu
	if not DEBUG:print('\033[H\033[J')
	print(' Contact Source')
	print('\t1. Directory');validOptions.append(1);options.insert(1,add_contact_from_directory)
	print('\t2. Contact Card');validOptions.append(2);options.insert(2,add_contact_from_card)
	print('\t0. Return To Previous Menu');validOptions.append(0);options.insert(0,do_nothing)

	#get user selection
	choice=get_valid_int(validOptions,' Selection: ')

	#choose option
	options[choice]()

	return False
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
	return False
	#end remove_contact

def update_addressbook():
	#begn update_addressbook
	if DEBUG:print('**update_addressbook under construction',line_number())
	global USER_NAME

	#end update_addressbook

def create_contact_card():
	#begin create_contact_card
	global USER_NAME
	if DEBUG:print('**prints to working directory, need to make desktop, relative',line_number())

	fileName='%s.card'%USER_NAME

	try:
		file=open(fileName,'w')
	except IOError:
		print(' Unable to create file %s,\n Contact Card Not Created\n'%fileName)
		return

	#generate hexstring from public key
	hexOfPubKey=USER_KEYS[0].encode(encoder=nacl.encoding.HexEncoder).decode()
	if DEBUG:print('key=%s'%hexOfPubKey)

	file.write(hexOfPubKey)
	file.close()

	print('Contact card creation successful')
	sleep(2)
	#end create_contact_card

def save_changes():
	#begin save_changes
	while True:
		save=input('Save changes? [y/n]: ')
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
		#display contacts
		display_contacts()

		#display edit contacts menu
		validOptions=[]
		options=[]
		print(' Edit contacts')
		print('\t1. Add Contact');validOptions.append(1);options.insert(1,add_contact)
		print('\t2. Remove Contact');validOptions.append(2);options.insert(2,remove_contact)
		print('\t3. Create Contact Card');validOptions.append(3);options.insert(3,create_contact_card)

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
		if options[choice]():break

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
		print(' Main Menu\n')
		print('\t1. Check Messages');validOptions.append(1);options.insert(1,check_messages)
		print('\t2. Send Message');validOptions.append(2);options.insert(2,send_message)
		print('\t3. Display Directory');validOptions.append(3);options.insert(3,display_directory)
		print('\t4. Display Addressbook'),validOptions.append(4);options.insert(4,display_contacts)
		print('\t5. Edit Contacts');validOptions.append(5);options.insert(5,edit_contacts)

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
