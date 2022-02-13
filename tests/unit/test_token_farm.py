import pytest
from brownie import network, exceptions
from web3 import Web3
from scripts.helpful_scripts import (
    DECIMALS,
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
    INITIAL_PRICE_FEED_VALUE,
    get_account,
    get_contract,
)
from scripts.deploy import deploy_nellarium_and_token_farm

# helper function tests
def test_set_price_feed_contract():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing...\n")

    account = get_account()
    non_owner_account = get_account(index=1)

    token_farm, nel_token = deploy_nellarium_and_token_farm()

    price_feed_address = get_contract("eth_usd_price_feed")

    # Act
    token_farm.setPriceFeedContract(
        nel_token.address, price_feed_address, {"from": account}
    )

    # Assert
    assert token_farm.tokenPriceFeedMapping(nel_token.address) == price_feed_address

    with pytest.raises(exceptions.VirtualMachineError):
        token_farm.setPriceFeedContract(
            nel_token.address, price_feed_address, {"from": non_owner_account}
        )


def test_token_is_allowed():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing...\n")

    account = get_account()

    token_farm, nel_token = deploy_nellarium_and_token_farm()

    # Act
    test_add_allowed_tokens()
    token_is_allowed = token_farm.tokenIsAllowed(nel_token, {"from": account})

    # Assert
    assert token_is_allowed == True


def test_get_user_total_staked_value(amount_staked, mock_erc20):
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing...\n")

    account = get_account()

    token_farm, nel_token = deploy_nellarium_and_token_farm()

    # Act
    add_txn = token_farm.addAllowedToken(mock_erc20.address, {"from": account})
    add_txn.wait(1)

    set_txn = token_farm.setPriceFeedContract(
        mock_erc20.address, get_contract("eth_usd_price_feed"), {"from": account}
    )
    set_txn.wait(1)

    stake_amount = amount_staked * 2
    approve_txn = mock_erc20.approve(
        token_farm.address, stake_amount, {"from": account}
    )
    approve_txn.wait(1)

    stake_txn = token_farm.stakeTokens(
        stake_amount, mock_erc20.address, {"from": account}
    )
    stake_txn.wait(1)

    # Assert
    total_eth_balance = token_farm.getUserTotalStakedValue(account)
    assert total_eth_balance == INITIAL_PRICE_FEED_VALUE * 2


def test_get_user_single_token_staked_value(amount_staked):
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing...\n")

    account = get_account()

    token_farm, nel_token = deploy_nellarium_and_token_farm()

    # Act
    approve_txn = nel_token.approve(
        token_farm.address, amount_staked, {"from": account}
    )
    approve_txn.wait(1)

    stake_txn = token_farm.stakeTokens(
        amount_staked, nel_token.address, {"from": account}
    )
    stake_txn.wait(1)

    token_value_eth = token_farm.getUserSingleTokenStakedValue(
        account, nel_token.address
    )

    # Assert
    assert token_value_eth == Web3.toWei("2000", "ether")


def test_get_token_value():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing...\n")

    account = get_account()

    token_farm, nel_token = deploy_nellarium_and_token_farm()

    # Act/Assert
    assert token_farm.getTokenValue(nel_token.address) == (
        INITIAL_PRICE_FEED_VALUE,
        DECIMALS,
    )


def test_add_allowed_tokens():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing...\n")

    account = get_account()
    non_owner_account = get_account(index=1)

    token_farm, nel_token = deploy_nellarium_and_token_farm()

    # Act
    token_farm.addAllowedToken(nel_token.address, {"from": account})

    # Assert
    assert token_farm.allowedTokens(0) == nel_token.address
    with pytest.raises(exceptions.VirtualMachineError):
        token_farm.addAllowedToken(nel_token.address, {"from": non_owner_account})


def test_stake_tokens(amount_staked):
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing...\n")

    account = get_account()

    token_farm, nel_token = deploy_nellarium_and_token_farm()

    # Act
    nel_token.approve(token_farm.address, amount_staked, {"from": account})

    token_farm.stakeTokens(amount_staked, nel_token.address, {"from": account})

    # Assert
    assert (
        token_farm.stakingBalance(nel_token.address, account.address) == amount_staked
    )
    assert token_farm.uniqueTokensStaked(account.address) == 1
    assert token_farm.stakers(0) == account.address

    return token_farm, nel_token


def test_stake_unapproved_token(amount_staked, mock_erc20):
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing...\n")

    account = get_account()

    token_farm, nel_token = deploy_nellarium_and_token_farm()

    # Act
    approve_txn = mock_erc20.approve(
        token_farm.address, amount_staked, {"from": account}
    )
    approve_txn.wait(1)

    # Assert
    with pytest.raises(exceptions.VirtualMachineError):
        token_farm.stakeTokens(amount_staked, mock_erc20.address, {"from": account})


def test_unstake_tokens(amount_staked):
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing...\n")

    account = get_account()

    token_farm, nel_token = test_stake_tokens(amount_staked)

    # Act
    token_farm.unstakeTokens(nel_token.address, {"from": account})

    # Assert
    assert nel_token.balanceOf(account.address) == Web3.toWei(100, "ether")
    assert token_farm.stakingBalance(nel_token.address, account.address) == 0
    assert token_farm.uniqueTokensStaked(account.address) == 0


def test_issue_tokens(amount_staked):
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing...\n")

    account = get_account()

    token_farm, nel_token = test_stake_tokens(amount_staked)

    starting_balance = nel_token.balanceOf(account.address)

    # Act
    token_farm.issueTokens({"from": account})

    val = token_farm.getUserSingleTokenStakedValue(
        account, nel_token.address, {"from": account}
    )

    print(f"\t\t{val}")

    # Assert
    # we are staking 1 NEL == in price to 1 ETH, so we should get 2000 NEL in reward, as the mock ETH/USD is $2000
    assert (
        nel_token.balanceOf(account.address)
        == starting_balance + INITIAL_PRICE_FEED_VALUE
    )
