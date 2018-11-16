#
#invoke: python3 chatChain.py [<True>]

import sys
from nacl.public import PrivateKey, Box
from nacl import secret, utils
import nacl.secret
from datetime import datetime
import binascii
import inspect
'''
# |                           bytes                              |    ciphertext     |    bytes    |
# | rx_encrypted_key | tx_encrypted_key | tx_pub_key | timestamp | timestamp+message | #recipients |
# |        72        |        72        |     64     |     26    |     variable      |      8      |

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
	if VERBOSE:print('len of ciphertext:',len(cipherText),line_number())

	#get user's key set and encrypt secret key
	userKeys=access_public_key_set() #retrieve public key set #should be using recipients key
	userPudKeyHex=userKeys[0].encode(encoder=nacl.encoding.HexEncoder) #make hex byte string of senders public key
	if VERBOSE:print('len of pub key:',userPudKeyHex,len(userPudKeyHex),type(userPudKeyHex),line_number()) #debug
	userBox=Box(userKeys[1],userKeys[0]) #make box to encrypt secret key for sender
	secretKeyForSenderCiphertext=userBox.encrypt(secretKey) #encrypt key for sender
	if VERBOSE:print('Encrypted key len:',len(secretKeyForSenderCiphertext),line_number())

	#get use public keys of recipients to encript secret key (need to be made into for loop for multiple recipients)
	recipientsPublicKeys=userKeys[0] #*****should be using passed in keys #hardcoded to send self message
	recvBox=Box(userKeys[1],recipientsPublicKeys) #make box to encrypt secret key for recipient
	secretKeyForRecipientCiphertext=recvBox.encrypt(secretKey) #encrypt key for recipient

	allKeys=secretKeyForRecipientCiphertext+secretKeyForSenderCiphertext #concat all keys

	cipherTextkeyMsg=(allKeys,cipherText) #make tuple of keys and cipherText

	return (cipherTextkeyMsg,timeStamp,userPudKeyHex) #return ciphertext and timestamp
	#end encrypt_message

def build_message_data(messageDataPlainText):
	#begin build_message_data
	#messageDataPlainText = (recipient,conversationID,message)
	global VERBOSE,NUMBER_OF_RECIPIENTS,MESSAGE_TEST #set variable to global scope
	if VERBOSE:print('Building_message_block',line_number()) #debugging output
	recipients,conversationID,message=messageDataPlainText #seperate tuple into individual variables
	numRecipients=bytes([NUMBER_OF_RECIPIENTS]) #make user definable later

	cipherTextkeyMsg,timeStamp,senderPubKey=encrypt_message(message,recipients) #turn message into ciphertext, also creates timestamp

	timeStamp=timeStamp.encode('ascii')#encodes timestamp to be added in plaintext

	#Concat and hex massage data for sending
	messageByteString=cipherTextkeyMsg[0]+timeStamp+cipherTextkeyMsg[1]+numRecipients #debug
	messageHexString=binascii.hexlify(cipherTextkeyMsg[0]+senderPubKey+timeStamp+cipherTextkeyMsg[1]+numRecipients)
	print('numRecipients bin added:',numRecipients,line_number())

	MESSAGE_TEST=messageByteString

	return messageHexString
	#end build_message_data

def parse_message_bin(messageBin):
	#begin parse_message_bin
	global VERBOSE
	if VERBOSE:print('\nParsing Message',line_number())

	encryptedKeyList=[]

	numberRecipients=int.from_bytes(messageBin[-1:],byteorder='big') #get number of recipients form end of message data
	if VERBOSE:print('numRecipients retrieved:',numberRecipients,type(numberRecipients),line_number()) #debug

	lengthOfKeys=((numberRecipients+1)*72)
	for x in range(0,lengthOfKeys,72):
		encryptedKeyList.append(messageBin[x:x+72]) #take slices from messageBin to get encrypted keys
	if VERBOSE:print('num keys found:',len(encryptedKeyList),line_number()) #debug

	senderPublicKey=messageBin[lengthOfKeys:(lengthOfKeys+64)]
	senderPublicKey=nacl.public.PublicKey(senderPublicKey,encoder=nacl.encoding.HexEncoder)
	if VERBOSE:print('recovered pub key:',type(senderPublicKey),line_number())

	plainTimestamp=messageBin[lengthOfKeys+64:(lengthOfKeys+64+26)].decode() #slice out timestamp
	if VERBOSE:print('Timestamp:',plainTimestamp,line_number())

	messageCiphertext=messageBin[(lengthOfKeys+64+26):-1] #get message ciphertext
	if VERBOSE:print('len message:',len(messageCiphertext),line_number())

	return (encryptedKeyList,plainTimestamp,messageCiphertext,numberRecipients,senderPublicKey)
	#end parse_message_bin

def decrypt_message(messageDataHexString):
	#begin decrypt_message
	global VERBOSE #set variable to global scope
	if VERBOSE:print('Decrypting_message',line_number()) #debug
	messageDataBytes=binascii.unhexlify(messageDataHexString) #translate message data from hex to bytes
	if VERBOSE:print('unhex:',messageDataBytes==MESSAGE_TEST,line_number()) #debug
	encryptedKeys,plaintextTimestamp,cipherText,numRecipients,senderPublicKey=parse_message_bin(messageDataBytes) #parse message into parts

	userPublicKey,userPrivateKey=access_public_key_set() #get user key set
	decryptKeyBox=Box(userPrivateKey,senderPublicKey) #box for decryption of secret key

	for each in encryptedKeys:
		secretKey=decryptKeyBox.decrypt(each) #decrypt key
		if VERBOSE:print('len Decrypted key:',len(secretKey),type(secretKey),line_number()) #debug
		print('check validity of test below',line_number()) #note
		if len(secretKey)==32: 
			secretBox=secret.SecretBox(secretKey) #make box for 
			plainText=secretBox.decrypt(cipherText) #get bytes of plaintext
			decryptedTimestamp=plainText[:26].decode() #extract timestamp from plaintext
			if VERBOSE:print('timeStamp comparison:',decryptedTimestamp==plaintextTimestamp) #debug
			if not decryptedTimestamp==plaintextTimestamp: #test for tampering
				print('Timestamps dont match: Tampering detected') #std out
				pass
			plainText=plainText[:19].decode()+'(UTC) '+plainText[26:].decode() #truncate timestamp add space
			if VERBOSE:print('plaintext:',plainText,line_number()) #debug
	return plainText #return plaintext from message
	#end decrypt_message

def check_messeges():
	#begin check_messeges
	print('check messages placeholder',line_number()) #todo
	pass
	#end check_messeges

def get_message_info():
	#begin get_message_info
	global GREETING, VERBOSE #set variable to global scope
	print(GREETING) #print greeting banner
	recipient=sanitize_input(input('Recipient Public Key: ')) #get recipient from user
	if VERBOSE:print('Echo Recipient:',recipient,line_number()) #debugging output
	conversationID=sanitize_input(input('\nConversation ID: ')) #get conversation ID from user
	if VERBOSE:print('Echo Conversation ID:',conversationID,line_number()) #debugging output
	message=sanitize_input(input('\nMessage: ')) #get message from user
	if VERBOSE:print('Echo Message: ',message,line_number()) #debugging output
	print('')
	return (recipient,conversationID,message) #return tuple of message attributes
	#end get_message_info

def main():
	#begin main
	global VERBOSE #set variable to global scope
	if len(sys.argv)>1: #check for args
		if sys.argv[1].lower()=='true': #check if detailed output desired
			print('Starting in Debug mode',line_number())
			VERBOSE=True
	if VERBOSE:print('Begin ChatChain',line_number()) #debugging output

	messageDataPlainText=get_message_info() #get message info from user
	messageDataHex=build_message_data(messageDataPlainText) #build the message for writting to chain

	if VERBOSE:print('\nHex:\n',messageDataHex,line_number()) #debug output
	print('')

	messageData=decrypt_message(messageDataHex)
	print(messageData,line_number())

	#end main

if __name__ == '__main__':
	main()
	if VERBOSE: print('End_of_program',line_number()) #debugging output
