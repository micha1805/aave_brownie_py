# AAVE staking with brownie

## Setup

As usual you need a `.env` file containing the following, adapted to your credentials :


```bash
export PRIVATE_KEY=0x1234567890
export WEB3_INFURA_PROJECT_ID=123456
export ETHERSCAN_TOKEN=ABCDEFGHIJKLMNOP

```

## What is this app doing ?



1. swap ETH for WETH (you need to use the wrapped version of ETH)
2. Deposit some ETH (WETH actually) into AAVE
3. Borrow some asset with the ETH collateral
    1. Sell that borrowed asset (Short)
4. Repay everything back


## Testing

Integration tests are done on the Kovan testnet

Local tests are done on Ganache

