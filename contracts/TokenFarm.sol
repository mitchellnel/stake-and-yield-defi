// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";

/// @title A stake-and-yield contract to be interacted with via web application
/// @dev The terms "user" and "staker" are used interchangeably
contract TokenFarm is Ownable {
    IERC20 nellarium;
    address[] public allowedTokens;

    /* details of users/stakers -- keeping track of:
        - balance of each token they have staked (token => staker => amt)
        - number of unique tokens they have staked (staker => amtOfUniqueTokens)
        - who the stakers are
    */
    mapping(address => mapping(address => uint256)) public stakingBalance;
    mapping(address => uint256) public uniqueTokensStaked;
    address[] public stakers;

    // mapping of tokens to their price feed addresses
    mapping(address => address) public tokenPriceFeedMapping;

    constructor(address _NellariumAddress) {
        nellarium = IERC20(_NellariumAddress);
    }

    /* core functions */
    function addAllowedToken(address _token) public onlyOwner {
        allowedTokens.push(_token);
    }

    function stakeTokens(uint256 _amount, address _token) public {
        // what tokens can they stake?
        require(
            tokenIsAllowed(_token),
            "Token you are trying to stake is not permitted to be staked."
        );

        // how much can they stake?
        require(_amount > 0, "Amount to stake must be greater than 0.");

        // user is staking a token
        updateUniqueTokensStaked(msg.sender, _token);

        // transfer tokens to our farm
        IERC20(_token).transferFrom(msg.sender, address(this), _amount);

        // update staker details in contract
        stakingBalance[_token][msg.sender] += _amount;

        if (uniqueTokensStaked[msg.sender] == 1) {
            stakers.push(msg.sender);
        }
    }

    function unstakeTokens(address _token) public {
        uint256 stakedBalance = stakingBalance[_token][msg.sender];
        require(stakedBalance > 0, "Staked balance cannot be 0.");

        IERC20(_token).transfer(msg.sender, stakedBalance);

        stakingBalance[_token][msg.sender] = 0; // re-entrancy attack?
        uniqueTokensStaked[msg.sender] -= 1;

        // remove msg.sender from stakers if they have no more staked tokens
        removeFromStakers(msg.sender);
    }

    function issueTokens() public onlyOwner {
        // issue tokens to all stakers
        for (uint256 i = 0; i < stakers.length; i++) {
            address recipient = stakers[i];

            // send recipient a token reward based on their total value locked
            uint256 userTotalStakedValue = getUserTotalStakedValue(recipient);
            nellarium.transfer(recipient, userTotalStakedValue);
        }
    }

    /* helper functions */
    function setPriceFeedContract(address _token, address _priceFeed)
        public
        onlyOwner
    {
        tokenPriceFeedMapping[_token] = _priceFeed;
    }

    function tokenIsAllowed(address _token) public view returns (bool) {
        for (uint256 i = 0; i < allowedTokens.length; i++) {
            if (allowedTokens[i] == _token) {
                return true;
            }
        }

        return false;
    }

    function updateUniqueTokensStaked(address _user, address _token) internal {
        if (stakingBalance[_token][_user] <= 0) {
            uniqueTokensStaked[_user] += 1;
        }
    }

    function getUserTotalStakedValue(address _user)
        public
        view
        returns (uint256)
    {
        uint256 totalStakedValue = 0;

        if (uniqueTokensStaked[_user] > 0) {
            for (uint256 i = 0; i < allowedTokens.length; i++) {
                totalStakedValue += getUserSingleTokenStakedValue(
                    _user,
                    allowedTokens[i]
                );
            }
        }

        return totalStakedValue;
    }

    /// @notice Get the USD value of a staker's specific staked token
    /// @param _user The address of the staker
    /// @param _token The address of the specific token we want to get the USD value for
    /// @return The USD value of _user's staked _token(s)
    function getUserSingleTokenStakedValue(address _user, address _token)
        public
        view
        returns (uint256)
    {
        if (uniqueTokensStaked[_user] <= 0) {
            // user has no tokens staked -- value is obviously 0
            return 0;
        }

        // usdValue = stakingBalance[_token][_user] * price of the token in USD
        (uint256 price, uint256 decimals) = getTokenValue(_token);

        return ((stakingBalance[_token][_user] * price) / (10**decimals));
    }

    /// @notice Get the USD value of a single unit (1) of a token, and the decimals of that token
    /// @param _token The address of the token we want the USD value for
    /// @return The USD value of 1 _token
    /// @return The decimals of _token
    function getTokenValue(address _token)
        public
        view
        returns (uint256, uint256)
    {
        address priceFeedAddress = tokenPriceFeedMapping[_token];

        AggregatorV3Interface priceFeed = AggregatorV3Interface(
            priceFeedAddress
        );

        (, int256 price, , , ) = priceFeed.latestRoundData();
        uint256 decimals = uint256(priceFeed.decimals());

        return (uint256(price), decimals);
    }

    /// @notice Remove a staker from the stakers list if they have no more unique tokens staked
    /// @param _user The address of the staker to potentially be removed
    function removeFromStakers(address _user) internal {
        if (uniqueTokensStaked[_user] <= 0) {
            // get the index of _user in stakers
            uint256 stakerIndex;
            for (uint256 i = 0; i < stakers.length; i++) {
                if (stakers[i] == _user) {
                    stakerIndex = i;
                    break;
                }
            }

            // move the last element of stakers into the place of the staker to be deleted
            stakers[stakerIndex] = stakers[stakers.length - 1]; // this essentially removes _user from stakers list

            // remove the last element -- no duplicates
            stakers.pop();
        }
    }
}
