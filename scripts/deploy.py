from brownie import config, network
from brownie import Nellarium, TokenFarm
from scripts.helpful_scripts import get_account, get_contract
from web3 import Web3

KEPT_BALANCE = Web3.toWei(100, "ether")


def deploy_nellarium():
    account = get_account()

    print("Deploying Nellarium token ...")
    nellarium = Nellarium.deploy({"from": account})
    print(f"... Done! Token contract can be found at {nellarium.address}\n")


def deploy_token_farm():
    account = get_account()

    nel_token = Nellarium[-1]

    print("Deploying TokenFarm ...")
    token_farm = TokenFarm.deploy(
        Nellarium[-1].address,
        {"from": account},
        publish_source=config["networks"][network.show_active()]["verify"],
    )
    print(f"... Done! TokenFarm contract can be found at {token_farm.address}\n")

    print(
        f"Transferring {(nel_token.totalSupply() - KEPT_BALANCE) / 10**18} NEL to the token farm ..."
    )
    txn = nel_token.transfer(token_farm.address, nel_token.totalSupply() - KEPT_BALANCE)
    txn.wait(1)
    print(f"... Done!\n")

    # we allow WETH, FAU (DAI), NEL
    weth_token = get_contract("weth_token")
    dai_token = get_contract("dai_token")
    allowed_tokens_dict = {
        nel_token: get_contract("dai_usd_price_feed"),
        dai_token: get_contract("dai_usd_price_feed"),
        weth_token: get_contract("eth_usd_price_feed"),
    }

    add_allowed_tokens(token_farm, allowed_tokens_dict, account)

    return token_farm, nel_token


def add_allowed_tokens(token_farm, allowed_tokens_dict, account):
    for token in allowed_tokens_dict:
        print(f"Adding token {token.name()} to the token farm ...")
        add_txn = token_farm.addAllowedToken(token.address, {"from": account})
        add_txn.wait(1)
        print("... Done! Token added.\n")

        print(f"Setting price feed for token {token.name()} ...")
        set_txn = token_farm.setPriceFeedContract(
            token.address, allowed_tokens_dict[token], {"from": account}
        )
        set_txn.wait(1)
        print("... Done! Price feed set.\n")


def main():
    deploy_nellarium()
    deploy_token_farm()
