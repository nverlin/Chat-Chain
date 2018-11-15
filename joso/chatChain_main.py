#
#invoke: python3 chatChain.py [<True>]

import sys
import nacl.utils
from nacl.public import PrivateKey, Box
import nacl.secret
from datetime import datetime
import binascii
import inspect
'''
# |                    bytes                        |    ciphertext     |    bytes    |
# | rx_encrypted_key | tx_encrypted_key | timestamp | timestamp+message | #recipients |
# |        72        |        72        |     26    |     variable      |      8      |

#encrypted keys bytes = (#recipients+1) * 72       # +1 is for the sender

#conversation ID to differentiate between conversations
#public key encryption to encrypt the secret key

#multi (later)
#number at beginning = num recipients
#encrypt key with each public key


TODO List:
	limit message size
	limit user input size
	move get input to func (<prompt>,<size>)-->get_user_input()-->()
	decrypt message
'''
VERBOSE=False
GREETING='\nWelcome to ChatChain\n'
NUMBER_OF_RECIPIENTS=1

def sanitize_input(inputString):
	#begin sanitize_input
	return inputString
	#end sanitize_input

def line_number():
	#begin line_number
	string='<ln:%i>'%inspect.currentframe().f_back.f_lineno
	return string
	#end line_number

def generate_timestamp():
	#begin generate_timestamp
	global VERBOSE
	if VERBOSE:print('Generating_timestamp',line_number())
	stamp=datetime.utcnow()
	if VERBOSE:print(stamp,line_number())
	return str(stamp)
	#end generate_timestamp

def generate_public_key_set():
	#begin generate_public_key_set
	privKey=PrivateKey.generate() #generate private key
	publKey=privKey.public_key #get public key	
	return (publKey,privKey) #return key set
	#end generate_public_key_set

def access_public_key_set():
	#begin access_public_key_set
	#should be changed to access from keystore later
	global VERBOSE #set variable to global scope
	if VERBOSE:print('Accessing_public_key_set',line_number()) #debugging output
	try: #open file convaining public key set
		file=open('keySet','rb')
	except IOError: #if file opening fails
		print('Failed_to_open file',line_number())
		exit()
	hexkey=file.read() #read key from file
	privKey=nacl.public.PrivateKey(hexkey,encoder=nacl.encoding.HexEncoder) #make read bytes into class privatekey
	file.close() #close file
	publKey=privKey.public_key #extract public key
	return (publKey,privKey) #return key set
	#end access_public_key_set

def encrypt_message(plaintextMessage,recipientsPublicKeys):
	#begin encrypt_message
	global VERBOSE #set variable to global scope
	if VERBOSE:print('Encrypting_message',line_number()) #debugging output

	secretKey=nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE) #generate secret key
	secretBox=nacl.secret.SecretBox(secretKey) #generate secret box

	#TIMESTAMP
	timeStamp=generate_timestamp() #get timestamp for message

	messageBytes=(timeStamp+plaintextMessage).encode('ascii') #convert string to bytes
	cipherText=secretBox.encrypt(messageBytes) #encrypt message

	#get user's key set and encrypt secret key
	userKeys=access_public_key_set() #retrieve public key set #should be using recipients key
	userBox=Box(userKeys[1],userKeys[0]) #make box to encrypt secret key for sender
	secretKeyForSenderCiphertext=userBox.encrypt(secretKey) #encrypt key for sender

	#get use public keys of recipients to encript secret key (need to be made into for loop for multiple recipients)
	recipientsPublicKeys=userKeys[0] #*****should be using passed in keys #hardcoded to send self message
	recvBox=Box(userKeys[1],recipientsPublicKeys) #make box to encrypt secret key for recipient
	secretKeyForRecipientCiphertext=recvBox.encrypt(secretKey) #encrypt key for recipient

	allKeys=secretKeyForRecipientCiphertext+secretKeyForSenderCiphertext #concat all keys

	cipherTextkeyMsg=(allKeys,cipherText) #make tuple of keys and cipherText

	return (cipherTextkeyMsg,timeStamp) #return ciphertext and timestamp
	#end encrypt_message

def build_message_data(messageDataPlainText):
	#begin build_message_data
	#messageDataPlainText = (recipient,conversationID,message)
	global VERBOSE,NUMBER_OF_RECIPIENTS #set variable to global scope
	if VERBOSE:print('Building_message_block',line_number()) #debugging output
	recipients,conversationID,message=messageDataPlainText #seperate tuple into individual variables
	numRecipients=bytes([NUMBER_OF_RECIPIENTS]) #make user definable later

	cipherTextkeyMsg,timeStamp=encrypt_message(message,recipients) #turn message into ciphertext, also creates timestamp

	timeStamp=timeStamp.encode('ascii')#encodes timestamp to be added in plaintext

	#Concat and hex massage data for sending
	messageByteString=cipherTextkeyMsg[0]+timeStamp+cipherTextkeyMsg[1]+numRecipients
	messageHexString=binascii.hexlify(cipherTextkeyMsg[0]+timeStamp+cipherTextkeyMsg[1]+numRecipients)

	return messageHexString
	#end build_message_data

def get_message_info():
	#begin get_message_info
	global GREETING, VERBOSE #set variable to global scope
	if VERBOSE:print('Getting_user',line_number()) #debugging output
	print(GREETING) #print greeting banner
	recipient=sanitize_input(input('Recipient Public Key: ')) #get recipient from user
	if VERBOSE:print('Echo Recipient:',recipient,line_number()) #debugging output
	conversationID=sanitize_input(input('Conversation ID: ')) #get conversation ID from user
	if VERBOSE:print('Echo Conversation ID:',conversationID,line_number()) #debugging output
	message=sanitize_input(input('Message: ')) #get message from user
	if VERBOSE:print('Echo Message: ',message,line_number()) #debugging output
	return (recipient,conversationID,message) #return tuple of message attributes
	#end get_message_info

def main():
	#begin main
	global VERBOSE #set variable to global scope
	user=None
	if len(sys.argv)>1: #check for args
		if sys.argv[1].lower()=='true': #check if detailed output desired
			print('Starting in Debug mode',line_number())
			VERBOSE=True
	if VERBOSE:print('Begin ChatChain',line_number()) #debugging output
	messageDataPlainText=get_message_info() #get message info from user
	messageDataHex=build_message_data(messageDataPlainText) #build the message for writting to chain
	if VERBOSE:print('\nHex:\n',messageDataHex,line_number()) #debug output
	#end main

if __name__ == '__main__':
	main()
	if VERBOSE: print('End_of_program',line_number()) #debugging output
