import json
import requests
import binascii
import types
import base64

def hex_prefix(value):
    if value[:2] == b'0x':
        return value
    return b'0x'+value

def to_hex(value):
    if isinstance(value, bytes):
        return hex_prefix(binascii.hexlify(value))
    if isinstance(value, str):
        if value == "true" or value == "True":
            return value.lower()
        if value == "false" or value == "False":
            return value.lower()
        return hex_prefix(binascii.hexlify(value.encode('utf-8')))
    if isinstance(value, int):
        return value


def convert_args(args):
    args = args or {}
    for k,v in args.items():
        args[k] = to_hex(v)
    return args


class Tendermint(object):
    def __init__(self, host=None):
        if host and not host[-1] == '/': host = host+'/'
        self.url = host or "http://localhost:26657/"

    def call(self, name, args=None):
        endpoint = '{}{}'.format(self.url, name)
        payload = convert_args(args)
        try:
            result = requests.get(endpoint, params=payload)
            return result.json()
        except ValueError as e:
            print('Error parsing response: {}'.format(e))
            return {'error': e.message}
    def status(self):
        return self.call('status')

    def info(self):
        return self.call('abci_info')

    def netinfo(self):
        return self.call('net_info')

    def genesis(self):
        return self.call('genesis')

    def broadcast_tx_commit(self,tx):
        return self.call('broadcast_tx_commit', {'tx': tx})

    def broadcast_tx_sync(self,tx):
	    return self.call('broadcast_tx_sync', {'tx': tx})

    def tx_search(self, query, prove, page, per_page):
        return self.call('tx_search', {'query': query, 'prove': prove, 'page': page, 'per_page': per_page})

    def blockchain(self,min, max):
        return self.call('blockchain', {'minHeight':min,'maxHeight':max})

    def block(self,height):
        return self.call('block', {'height':height})

    def commit(self, height):
        return self.call('commit', {'height':height})

    def query(self, path,data,prove):
        return self.call('abci_query', {'path': path, 'data':data, 'prove': prove})

    def get_message_blockchain(self, id):
        key = "app.key='" + id + "'"
        result = list()
        data = self.tx_search(key, "true", 100, 100)

        for element in data['result']['txs']:
            result.append(base64.b64decode(element['tx']).split(b'=')[1])
        
        return result
     def get_status(self):
        data = self.status()
        result = data['result']['sync_info']['catching_up']
        if result == 'False':
            return False
        else:
            return True


