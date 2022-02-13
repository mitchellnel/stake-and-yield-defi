from audioop import add
from brownie import accounts, config, network, interface, Contract
from brownie import MockV3Aggregator, MockDAI, MockWETH
from web3 import Web3

LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-local"]
FORKED_LOCAL_ENVIRONMENTS = ["mainnet-fork", "mainnet-fork-dev"]

CONTRACT_TO_MOCK = {
    "eth_usd_price_feed": MockV3Aggregator,
    "dai_usd_price_feed": MockV3Aggregator,
    "dai_token": MockDAI,
    "weth_token": MockWETH,
}

DECIMALS = 18
INITIAL_PRICE_FEED_VALUE = 2000_000000000000000000


def get_account(index=None, id=None):
    if index is not None:
        return accounts[index]
    elif id is not None:
        return accounts.load(id)
    elif (
        network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS
        or network.show_active() in FORKED_LOCAL_ENVIRONMENTS
    ):
        return accounts[0]
    else:
        return accounts.add(config["wallets"]["from_key"])


def get_contract(contract_name):
    """Returns the contract address from the Brownie config if it is defined.
    Otherwise, it will deploy a mock version of the contract, and return the
        mock contract.

    Keyword arguments:
    - contract_name -- the name of the contract that we are looking to interact with

    Returns:
    a brownie.network.contract.ProjectContract object, which is the most recently
        deployed Contract of the type specified by the dictionary. This could either
        be a mock contract or a real contract deployed on a live network.
    """
    contract_type = CONTRACT_TO_MOCK[contract_name]

    # do we need to deploy a mock?
    if (
        network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS
        or network.show_active() in FORKED_LOCAL_ENVIRONMENTS
    ):
        if len(contract_type) <= 0:
            deploy_mocks()
        contract = contract_type[-1]
    else:
        # use address and ABI to create contract object
        contract_address = config["networks"][network.show_active()][contract_name]

        contract = Contract.from_abi(
            contract_type._name, contract_address, contract_type.abi
        )

    return contract


def deploy_mocks(decimals=DECIMALS, initial_value=INITIAL_PRICE_FEED_VALUE):
    """Deploys mock contracts to a testnet."""
    account = get_account()
    print(f"The active network is {network.show_active()}")
    print("Deploying mocks...")

    print("... Deploying Mock Price Feed ...")
    price_feed = MockV3Aggregator.deploy(decimals, initial_value, {"from": account})
    print(f"... Mock Price Feed deployed to {price_feed.address} ...")

    print("... Deploying Mock DAI Token ...")
    dai_token = MockDAI.deploy({"from": account})
    print(f"... Mock DAI deployed to {dai_token.address} ...")

    print("... Deploying Mock WETH Token ...")
    weth_token = MockWETH.deploy({"from": account})
    print(f"... Mock WETH deployed to {weth_token.address} ...")

    print(f"... Done! All mocks deployed.\n")
