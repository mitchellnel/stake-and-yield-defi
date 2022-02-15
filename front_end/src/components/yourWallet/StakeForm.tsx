import { useEthers, useTokenBalance } from "@usedapp/core";
import { formatUnits } from "@ethersproject/units";
import { Button, Input } from "@material-ui/core";
import React, { useState } from "react";
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

    const [amount, setAmount] = useState<
        number | string | Array<number | string>
    >(0);
    const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        const newAmount =
            event.target.value === "" ? "" : Number(event.target.value);
        setAmount(newAmount);
        console.log("Input amount to stake is %d", newAmount);
    };

    const { approveAndStake, approveERC20State } = useStakeTokens(tokenAddress);

    const handleStakeSubmit = () => {
        const amountAsWei = utils.parseEther(amount.toString());

        return approveAndStake(amountAsWei.toString());
    };

    return (
        <>
            <Input onChange={handleInputChange} />

            <Button onClick={handleStakeSubmit} color="primary" size="large">
                Stake!!!
            </Button>
        </>
    );
};
