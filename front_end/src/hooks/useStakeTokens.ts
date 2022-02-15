import { useState, useEffect } from "react";
import { useEthers, useContractFunction } from "@usedapp/core";
import { constants, utils } from "ethers";
import { Contract } from "@ethersproject/contracts";

import TokenFarm from "../chain-info/contracts/TokenFarm.json";
import ERC20 from "../chain-info/contracts/MockERC20.json";
import networkMapping from "../chain-info/deployments/map.json";

export const useStakeTokens = (tokenAddress: string) => {
    const { chainId } = useEthers();

    // get TokenFarm contract
    const { abi } = TokenFarm;
    const tokenFarmAddress = chainId
        ? networkMapping[String(chainId)]["TokenFarm"][0]
        : constants.AddressZero;
    const tokenFarmInterface = new utils.Interface(abi);
    const tokenFarmContract = new Contract(
        tokenFarmAddress,
        tokenFarmInterface
    );

    // get ERC20 contract
    const erc20ABI = ERC20.abi;
    const erc20Interface = new utils.Interface(erc20ABI);
    const erc20Contract = new Contract(tokenAddress, erc20Interface);

    // make the approve transaction
    const { send: approveERC20Send, state: approveERC20State } =
        useContractFunction(erc20Contract, "approve", {
            transactionName: "Approve ERC20 Transfer",
        });

    const approveAndStake = (amount: string) => {
        setAmountToStake(amount);
        return approveERC20Send(tokenFarmAddress, amount);
    };

    const [amountToStake, setAmountToStake] = useState("0");

    // if approve transaction is successful, make the stake transaction
    const { send: stakeSend, state: stakeState } = useContractFunction(
        tokenFarmContract,
        "stakeTokens",
        { transactionName: "Stake Tokens" }
    );

    useEffect(() => {
        if (approveERC20State.status === "Success") {
            // perform the stake function
            stakeSend(amountToStake, tokenAddress);
        }
    }, [approveERC20State, amountToStake, tokenAddress]);

    // track overall state
    const [state, setState] = useState(approveERC20State);

    useEffect(() => {
        if (approveERC20State.status === "Success") {
            setState(stakeState);
        } else {
            setState(approveERC20State);
        }
    }, [approveERC20State, stakeState]);

    return { approveAndStake, state };
};
