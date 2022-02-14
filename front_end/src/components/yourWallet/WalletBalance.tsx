import { useEthers, useTokenBalance } from "@usedapp/core"
import { formatUnits } from "@ethersproject/units"

import { Token } from "../Main"
import { BalanceMsg } from "../BalanceMsg"

interface WalletBalanceProps {
    token: Token
}

export const WalletBalance = ({ token }: WalletBalanceProps) => {
    const { image, address, name } = token
    const { account } = useEthers()

    const tokenBalance = useTokenBalance(address, account)
    const formattedTokenBalance: number = tokenBalance ? parseFloat(formatUnits(tokenBalance, 18)) : 0
    console.log("%s balance is %d", name, formattedTokenBalance)

    return (<BalanceMsg
        label={`Your un-staked ${name} balance`}
        tokenImgSrc={image}
        amount={formattedTokenBalance} />
    )
}
