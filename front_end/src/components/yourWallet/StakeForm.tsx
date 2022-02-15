import { useEthers, useTokenBalance, useNotifications } from "@usedapp/core";
import { formatUnits } from "@ethersproject/units";
import { Button, Input, CircularProgress } from "@material-ui/core";
import React, { useEffect, useState } from "react";
import { utils } from "ethers";

import { Token } from "../Main";
import { useStakeTokens } from "../../hooks/useStakeTokens";

interface StakeFormProps {
    token: Token;
}

export const StakeForm = ({ token }: StakeFormProps) => {
    const { address: tokenAddress, name } = token;
    const { account } = useEthers();

    const tokenBalance = useTokenBalance(tokenAddress, account);
    const formattedTokenBalance: number = tokenBalance
        ? parseFloat(formatUnits(tokenBalance))
        : 0;

    // notification handling -- printing to console
    const { notifications } = useNotifications();

    useEffect(() => {
        if (
            notifications.filter(
                (notification) =>
                    notification.type === "transactionSucceed" &&
                    notification.transactionName === "Approve ERC20 Transfer"
            ).length > 0
        ) {
            console.log("Approved!");
        }

        if (
            notifications.filter(
                (notification) =>
                    notification.type === "transactionSucceed" &&
                    notification.transactionName === "Stake Tokens"
            ).length > 0
        ) {
            console.log("Tokens staked!");
        }
    }, [notifications]);

    // input event handler
    const [amount, setAmount] = useState<
        number | string | Array<number | string>
    >(0);
    const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        const newAmount =
            event.target.value === "" ? "" : Number(event.target.value);
        setAmount(newAmount);
        console.log("Input amount to stake is %d", newAmount);
    };

    // contract interactions
    const { approveAndStake, state: approveAndStakeState } =
        useStakeTokens(tokenAddress);

    const handleStakeSubmit = () => {
        const amountAsWei = utils.parseEther(amount.toString());

        return approveAndStake(amountAsWei.toString());
    };

    // front-end for "notificaiton" monitoring -- i.e. show loading
    const isMining = approveAndStakeState.status === "Mining";

    // front-end return
    return (
        <>
            <Input onChange={handleInputChange} />

            <Button
                onClick={handleStakeSubmit}
                color="primary"
                size="large"
                disabled={isMining}
            >
                {isMining ? <CircularProgress size={26} /> : "Stake!!!"}
            </Button>
        </>
    );
};
