from brownie import Lottery, accounts, config, network, exceptions

# external
from web3 import Web3
import pytest

# internal
from scripts.deploy_lottery import deploy_lottery
from scripts.helpful_scripts import LOCAL_BLOCKCHAIN_ENVIRONMENTS, fund_with_link, get_account, get_contract

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

def test_cant_enter_unless_started():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_lottery()    

    # Act/Assert
    with pytest.raises(exceptions.VirtualMachineError):
        lottery.enter({'from': get_account(), 'value': lottery.getEntranceFee()})

def test_can_start_and_enter_lottery():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({'from': account})

    # Act
    lottery.enter({'from': account, 'value': lottery.getEntranceFee()})

    # Assert
    assert lottery.players(0) == account

def test_can_end_lottery():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({'from': account})

    # Act
    lottery.enter({'from': account, 'value': lottery.getEntranceFee()})
    fund_with_link(lottery.address)
    lottery.endLottery({'from': account})
    assert lottery.lottery_state() == 2

def test_can_pick_winner_correctly():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({'from': account})
    lottery.enter({'from': account, 'value': lottery.getEntranceFee()})
    lottery.enter({'from': get_account(1), 'value': lottery.getEntranceFee()})
    lottery.enter({'from': get_account(2), 'value': lottery.getEntranceFee()})
    fund_with_link(lottery.address)

    # Act?
    starting_balance_of_account = account.balance()
    balance_of_lottery = lottery.balance()
    transaction = lottery.endLottery({'from': account})
    request_id = transaction.events['RequestedRandomness']['requestId']
    STATIC_RNG = 777
    get_contract("vrf_coordinator").callBackWithRandomness(
        request_id, STATIC_RNG, lottery.address, {"from": account}
    )
    # 777 % 3 = 0 therefore 0 index player is the winner

    # Assert
    assert lottery.recentWinner() == account 
    assert lottery.balance() == 0
    assert account.balance() == starting_balance_of_account + balance_of_lottery