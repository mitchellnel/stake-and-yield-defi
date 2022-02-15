import { useEthers } from "@usedapp/core";
import { constants } from "ethers";

import helperConfig from "../helper-config.json";
import networkMapping from "../chain-info/deployments/map.json";
import brownieConfig from "../brownie-config.json";

import nel from "../nel.png";
import weth from "../eth.png";
import dai from "../dai.png";

import { YourWallet } from "./yourWallet";

export type Token = {
    image: string;
    address: string;
    name: string;
};

export const Main = () => {
    // show token values from the wallet

    // get the address of different tokens

    // get the balance of the user's wallet

    // send brownie-config.yaml to our src/ folder

    // send the build folder

    // work out what chain we're working on
    const { chainId } = useEthers();
    const networkName = chainId ? helperConfig[chainId] : "dev";
    console.log("Chain ID: %d\nNetwork Name: %s", chainId, networkName);

    // get the addresses of different tokens
    const nelTokenAddress = chainId
        ? networkMapping[String(chainId)]["Nellarium"][0]
        : constants.AddressZero;
    const wethTokenAddress = chainId
        ? brownieConfig["networks"][networkName]["weth_token"]
        : constants.AddressZero;
    const daiTokenAddress = chainId
        ? brownieConfig["networks"][networkName]["dai_token"]
        : constants.AddressZero;

    // show token values from the wallet
    const supportedTokens: Array<Token> = [
        {
            image: nel,
            address: nelTokenAddress,
            name: "NEL",
        },
        {
            image: weth,
            address: wethTokenAddress,
            name: "WETH",
        },
        {
            image: dai,
            address: daiTokenAddress,
            name: "DAI",
        },
    ];

    return <YourWallet supportedTokens={supportedTokens} />;
};
