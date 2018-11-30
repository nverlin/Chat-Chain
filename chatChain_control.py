# Author: Joseph Soares
# file: chatChain_control.py
# purpose: contains main control loop for program
# invoke: python3 chatChain_control.py

#imports
from chatChain_main import *

def line_number():
	#begin line_number
	string='<ln:%i>'%inspect.currentframe().f_back.f_lineno
	return string
	#end line_number

def send_message():
	#begin send_message
	pass
	#endsend_message

def authenticate_user():
	#begin authenticate_user
	pass
	#end authenticate_user

def main_menu():
	#begin main_menu
	while True:
		print('\n1. Check Messages')
		print('2. Send Message')
		print('3. Display Contacts')
		print('4. Edit Contacts')

		print('0. Exit ChatChain\n')

		choice=int(input('Selection: '))
		if choice==0:
			print('\nThank you for using ChatChain')
			exit()
		elif choice==2:
			send_message()


	pass
	#end main_menu

def greet_user():
	#begin greet_user
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
	authenticate_user()
	greet_user()
	main_menu()
	pass
	#end main

if __name__ == '__main__':
	main()