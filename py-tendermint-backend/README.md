# Python Tendermint client (HTTP)

### Install
Tendermint version 0.26.0

Requires Python 3.6

Recommend [PipEnv](http://docs.pipenv.org/en/latest/) for a virtualenv but not required
```
git clone https://github.com/davebryson/py-tendermint-client
cd py-tendermint-client
pipenv --three # for a python 3 virtualenv
pipenv install
```

### Try it out
```
Start the tendermint node
>> tendermint node

In another terminal run the kvstore app
>> tendermint node --proxy_app=kvstore

In another fire up a console
>> python3
>>> from tendermint import Tendermint
>>> t = Tendermint()
>>> t.status()
>>> t.broadcast_tx_commit('helloworld')
>>> t.query("", "helloworld", "true") # function requires 3 parameters (path, data, prove)
```
