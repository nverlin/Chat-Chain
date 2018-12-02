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
	testhexstring1='8660147153714c5ccf692478119593162167e8c4d0151972bbfb060e10bb79c2d49d81a81f60120bd1213161e413096b44e6ca3d5ff685837679a078cc525a0cb7be01914c6674a110e243a7e6dc91462e726de8aa41e26e2f6e4b11b309c98f79dcf6fbf0467e09154eb1cea71dd949035b52d28c99af01aecacd3383ff2bf66ffd53804c3f282e28cdf212fe4eba2a84890e1504e050edb0bb96b26d9a3d62e057e8ed28201513903d9268b71f82a121c331d9c610a5b778f2d8b2eb1b4b48a6175f64fe764adc5b32e5ea05dd173422b2d1d5accd14e630343039373864383834386638356638623930333031663761383762353161386432333466393763343133393633306162646433303932363561303936383264323031382d31322d30322031383a34343a30342e30343235383781b2ff293e71003620863e4c1a8d142a8e2861a040ea934e9b8ae4c12cd2b6cdbfef4add1465019ae6e428c6e0d019f86dbfbb09359ee4c733ef96e53f945ef66d9184bc2746f287083d31686c02'
	
	file=open('test','r')
	testhexstring2=file.readline().rstrip()
	file.close()
	print(testhexstring1==testhexstring2,line_number())
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
	global BLOCK
	#initialize and sync blockchain instance
	#create instance
	BLOCK=tendermint.Tendermint()
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