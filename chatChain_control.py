# Author: Joseph Soares
# file: chatChain_control.py
# purpose: contains main control loop for program
# invoke: python3 chatChain_control.py

#imports
from chatChain_main import *
#from py-tendermint-bachend.tendermint.backend import *
#tendermint=__import__('py-tendermint-backend/tendermint/backend')
import importlib
tendermint=importlib.import_module('py-tendermint-backend.tendermint.backend')
import time

#globals
GREETING='Welcome to ChatChain'
ADDRESSBOOK={}
USER_KEYS=None

def line_number():
	#begin line_number
	string='<%s>'%sys.argv[0]+'<ln:%i>'%inspect.currentframe().f_back.f_lineno
	return string
	#end line_number

def send_message():
	#begin send_message
	messageInfo=get_message_info(ADDRESSBOOK) #return (<keys>, <conversation ID>, <message>)
	print(messageInfo,line_number())
	messageData=build_message_data(messageInfo,USER_KEYS)
	#endsend_message

def load_addressbook(addressbookData):
	#begin load_addressbook
	global ADDRESSBOOK	

	for datum in addressbookData:
		datum=datum.rstrip().split(',')
		ADDRESSBOOK[datum[1]]=nacl.public.PrivateKey(datum[0],encoder=nacl.encoding.HexEncoder).public_key

	# for each in ADDRESSBOOK:
	# 	print(each,type(ADDRESSBOOK[each]))
	#end load_addressbook

def get_user_keys(keyString):
	#begin get_user_keys
	keySet=nacl.public.PrivateKey(keyString,encoder=nacl.encoding.HexEncoder)
	return (keySet.public_key,keySet)
	#end get_user_keys

def setup_user():
	#begin setup_user
	global USER_KEYS

	#authenticate user func from Nathat, should return contents of user file
	print('loading temp userFile',line_number())
	file=open('userFile','r')
	userData=file.readlines()
	file.close()

	USER_KEYS=get_user_keys(userData[0].rstrip()) #*(publKey,privKey)*

	load_addressbook(userData[1:])
	#end setup_user

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
				choice=int(input('Selection: '))
			except ValueError:
				print('Invalid Entry')
				continue

			if choice not in validOptions:print('Invalid Entry');continue
			break
		
		if choice==0:
			print('\n Thank you for using ChatChain\n')
			time.sleep(2)
			exit()
		elif choice==2:
			send_message()

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
	#initialize and sync blockchain instance
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