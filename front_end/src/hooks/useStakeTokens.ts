import React, { useState } from "react"
import { useEthers, useContractFunction } from "@usedapp/core"
import { constants, utils } from "ethers"
import { Contract } from "@ethersproject/contracts"

import TokenFarm from "../chain-info/contracts/TokenFarm.json"
import ERC20 from "../chain-info/contracts/MockERC20.json"
import networkMapping from "../chain-info/deployments/map.json"


export const useStakeTokens = (tokenAddress: string) => {
    const { chainId } = useEthers()

    // get TokenFarm contract
    const { abi } = TokenFarm
    const tokenFarmAddress = chainId ? networkMapping[String(chainId)]["TokenFarm"][0] : constants.AddressZero
    const tokenFarmInterface = new utils.Interface(abi)
    const tokenFarmContract = new Contract(tokenFarmAddress, tokenFarmInterface)

    // get ERC20 contract
    const erc20ABI = ERC20.abi
    const erc20Interface = new utils.Interface(erc20ABI)
    const erc20Contract = new Contract(tokenAddress, erc20Interface)

    // make the approve transaction
    const { send: approveERC20Send, state: approveERC20State } =
        useContractFunction(
            erc20Contract, "approve", { transactionName: "Approve ERC20 Transfer" }
        )

    const approve = (amount: string) => {
        return approveERC20Send(tokenFarmAddress, amount)
    }

    const [state, setState] = useState(approveERC20State)

    return { approve, approveERC20State }
}
