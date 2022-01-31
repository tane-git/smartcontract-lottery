from brownie import Lottery, accounts, config, network, exceptions

# external
from web3 import Web3
import pytest

# internal
from scripts.deploy_lottery import deploy_lottery
from scripts.helpful_scripts import LOCAL_BLOCKCHAIN_ENVIRONMENTS, get_account

def test_get_entrance_fee():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()

    # NEW TEST:
    # arrange
    lottery = deploy_lottery()

    # act
    entrance_fee = lottery.getEntranceFee()
    expected_entrance_fee = Web3.toWei(0.025, 'ether')

    #assert
    print('difference', entrance_fee - expected_entrance_fee)
    print(entrance_fee)
    print(expected_entrance_fee)
    assert expected_entrance_fee == entrance_fee

def cant_enter_unless_starter():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_lottery()    
    with pytest.raises(exceptions.VirtualMachineError):
        lottery.enter({'from': get_account(), 'value': lottery.getEntranceFee()})
