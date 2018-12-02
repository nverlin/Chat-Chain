# Author: Joseph Soares
#invoke: python3 chatChain.py [<True>]

#imports
import sys
from nacl.public import PrivateKey, Box
from nacl import secret, utils
import nacl.secret
from datetime import datetime
import binascii
import inspect

#message breakdown
'''
# |                             bytes                                |    ciphertext     |    bytes    |
# | rx_encrypted_key | tx_encrypted_key | tx_pub_key_hex | timestamp | timestamp+message | #recipients |
# |        72        |        72        |       64       |     26    |     variable      |      8      |

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

#globals
VERBOSE=False

def sanitize_input(inputString):
	#begin sanitize_input
	return inputString
	#end sanitize_input

def line_number():
	#begin line_number
	string='<%s>'%sys.argv[0]+'<ln:%i>'%inspect.currentframe().f_back.f_lineno
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

def encrypt_message(plaintextMessage,recipientsPublicKeys,userKeys):
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

	#encrypt secret key for sender get bytestring of hex of sender pubkey *(publKey,privKey)*
	userPubKeyHex=userKeys[0].encode(encoder=nacl.encoding.HexEncoder) #make hex byte string of senders public key
	if VERBOSE:print('len of pub key:',userPubKeyHex,len(userPubKeyHex),type(userPubKeyHex),line_number()) #debug
	userBox=Box(userKeys[1],userKeys[0]) #make box to encrypt secret key for sender
	secretKeyForSenderCiphertext=userBox.encrypt(secretKey) #encrypt key for sender
	if VERBOSE:print('Encrypted key len:',len(secretKeyForSenderCiphertext),line_number())

	#use public keys of recipients to encrypt secret key (need to be made into for loop for multiple recipients)
	secretKeyForRecipientCiphertext=b''
	for recipKey in recipientsPublicKeys:
		recvBox=Box(userKeys[1],recipKey) #make box to encrypt secret key for recipient
		secretKeyForRecipientCiphertext+=recvBox.encrypt(secretKey) #encrypt key for recipient

	allKeys=secretKeyForRecipientCiphertext+secretKeyForSenderCiphertext #concat all keys

	cipherTextkeyMsg=(allKeys,cipherText) #make tuple of keys and cipherText

	return (cipherTextkeyMsg,timeStamp,userPubKeyHex) #return ciphertext and timestamp
	#end encrypt_message

def build_message_data(messageDataPlainText,userKeys):
	#begin build_message_data
	#messageDataPlainText = (recipient,conversationID,message)
	global VERBOSE,MESSAGE_TEST #set variable to global scope
	if VERBOSE:print('Building_message_block',line_number()) #debugging output
	recipients,conversationID,message,numRecipients=messageDataPlainText #seperate tuple into individual variables
	numRecipients=bytes([numRecipients])
	#numRecipients=bytes([NUMBER_OF_RECIPIENTS]) #make user definable later

	cipherTextkeyMsg,timeStamp,senderPubKeyHex=encrypt_message(message,recipients,userKeys) #turn message into ciphertext, also creates timestamp

	timeStamp=timeStamp.encode('ascii') #encodes timestamp to be added in plaintext

	#Concat and hex message data for sending
	messageHexString=binascii.hexlify(cipherTextkeyMsg[0]+senderPubKeyHex+timeStamp+cipherTextkeyMsg[1]+numRecipients)
	print('numRecipients bin added:',numRecipients,line_number())

	return messageHexString.decode()
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

def decrypt_message(messageDataHexString,userKeySet):
	#begin decrypt_message
	global VERBOSE #set variable to global scope
	if VERBOSE:print('Decrypting_message',line_number()) #debug
	messageDataBytes=binascii.unhexlify(messageDataHexString) #translate message data from hex to bytes
	if VERBOSE:print('unhex:',messageDataBytes==MESSAGE_TEST,line_number()) #debug
	encryptedKeys,plaintextTimestamp,cipherText,numRecipients,senderPublicKey=parse_message_bin(messageDataBytes) #parse message into parts

	userPublicKey,userPrivateKey=userKeySet #get user key set
	decryptKeyBox=Box(userPrivateKey,senderPublicKey) #box for decryption of secret key

	notAuthorized=True
	for each in encryptedKeys:
		try:
			secretKey=decryptKeyBox.decrypt(each) #decrypt key
			notAuthorized=False
			print('good key',line_number())
		except:
			print('bad key',line_number())
			continue
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
	if notAuthorized:plainText=plaintextTimestamp[:19]+'(UTC) Not Authorized to decrypt.'
	plainText=plaintextTimestamp[:19]+'(UTC) Not Authorized to decrypt.'
	return plainText #return plaintext from message
	#end decrypt_message

def check_messeges():
	#begin check_messeges
	print('check messages placeholder',line_number()) #todo
	pass
	#end check_messeges

def get_recipients(addressbook):
	#begin get_recipients
	selections={}
	count=1
	validOptions=[]
	recipientKeys=[]

	#get number of recipients from user
	while 1:
		try:
			numRecipients=int(input('Number of Recipients: '))
		except ValueError:
			print('Invalid Entry')
			continue
		break

	#print the addressbook
	print(' Contacts')
	for entry in addressbook:
		print('\t%i. %s'%(count,entry))
		validOptions.append(count)
		selections[count]=entry
		count+=1

	#choose recipients from addressbook
	for x in range(numRecipients):
		while 1:
			try:
				choice=int(input('Selection %i: '%(x+1)))
			except ValueError:
				print('Invalid Entry')
				continue
			if choice not in validOptions:
				print('Invalid Entry')
				continue
			recipientKeys.append(addressbook[selections[choice]])
			break

	return (recipientKeys,numRecipients)
	#end get_recipients

def get_message_info(addressbook):
	#begin get_message_info
	global VERBOSE #set variable to global scope
	recipients,numRecipients=get_recipients(addressbook)
	conversationID=sanitize_input(input('\nConversation ID: ')) #get conversation ID from user
	if VERBOSE:print('Echo Conversation ID:',conversationID,line_number()) #debugging output
	message=sanitize_input(input('\nMessage: ')) #get message from user
	if VERBOSE:print('Echo Message: ',message,line_number()) #debugging output
	print('')
	return (recipients,conversationID,message,numRecipients) #return tuple of message attributes
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
