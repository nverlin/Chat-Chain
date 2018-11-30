from tendermint import Tendermint

def test_json():
    t = Tendermint()
    print(t.status())
