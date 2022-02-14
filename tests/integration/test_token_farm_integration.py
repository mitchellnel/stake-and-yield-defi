import pytest
from brownie import network
from scripts.helpful_scripts import (
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
    get_account,
    get_contract,
)
from scripts.deploy import deploy_nellarium_and_token_farm


def test_stake_and_issue_correct_amounts(amount_staked):
    # Arrange
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for integration testing...\n")

    account = get_account()

    token_farm, nel_token = deploy_nellarium_and_token_farm()

    price_feed_contract = get_contract("eth_usd_price_feed")

    approve_txn = nel_token.approve(
        token_farm.address, amount_staked, {"from": account}
    )
    approve_txn.wait(1)

    stake_txn = token_farm.stakeTokens(
        amount_staked, nel_token.address, {"from": account}
    )
    stake_txn.wait(1)

    starting_balance = nel_token.balanceOf(account.address)

    (_, price, _, _, _) = price_feed_contract.latestRoundData()
    amount_token_to_issue = (
        price / (10 ** price_feed_contract.decimals())
    ) * amount_staked

    # Act
    issue_txn = token_farm.issueTokens({"from": account})
    issue_txn.wait(1)

    # Assert
    assert (
        nel_token.balanceOf(account.address) == amount_token_to_issue + starting_balance
    )
