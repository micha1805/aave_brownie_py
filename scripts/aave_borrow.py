from brownie import network, config, interface, accounts
from scripts.helpful_scripts import get_account
from scripts.get_weth import get_weth
from web3 import Web3


# 0.1
# amount = 100000000000000000 #Wei
amount = Web3.toWei(0.1, "ether")


def repay_all(amountInWei, lending_pool, account):
    approve_erc20_token(
        amountInWei,
        lending_pool,
        config["networks"][network.show_active()]["dai_token"],
        account,
    )
    # function repay(address asset, uint256 amount, uint256 rateMode, address onBehalfOf)
    repay_tx = lending_pool.repay(
        config["networks"][network.show_active()]["dai_token"],
        amountInWei,
        1,
        account.address,
        {"from": account},
    )
    repay_tx.wait(1)
    print("Repaid!")


def get_asset_price(price_feed_address):
    # ABI
    # Address
    dai_eth_price_feed = interface.AggregatorV3Interface(price_feed_address)
    latest_price = dai_eth_price_feed.latestRoundData()[1]
    # dans la doc il est mis que cela retourne un nombre de 18 décimales,
    # il suffit de diviser par 1e18 et l'on obtient le vrai nombre.
    # Ou bien on utilise Web3.fromWei(latest_price, "ether")
    latest_price_in_usual_units = latest_price / 1e18
    # latest_price_in_usual_units = Web3.fromWei(latest_price, "ether")
    print(f"The latest DAI/ETH price is {latest_price_in_usual_units}")
    return float(latest_price_in_usual_units)


def get_borrowable_data(lending_pool, account):
    # All of these are in WEI, except health factor obviously
    (
        total_collateral_eth,
        total_debt_eth,
        available_borrow_eth,
        current_liquidation_treshold,
        ltv,
        health_factor,
    ) = lending_pool.getUserAccountData(account.address)
    # let's conert them back to ETH
    available_borrow_eth = Web3.fromWei(available_borrow_eth, "ether")
    total_collateral_eth = Web3.fromWei(total_collateral_eth, "ether")
    total_debt_eth = Web3.fromWei(total_debt_eth, "ether")
    print(f"You have {total_collateral_eth} worth of ETH deposited")
    print(f"You have {total_debt_eth} worth of ETH borrowed")
    print(f"You can borrow {available_borrow_eth} worth of ETH")
    # float is added to avoid problem in later calculations:
    return (float(available_borrow_eth), float(total_debt_eth))


def approve_erc20_token(amount, spender, erc20_address, account):
    print("Approving ERC20 token ...")
    # ABI
    # address
    erc20 = interface.IERC20(erc20_address)
    tx = erc20.approve(spender, amount, {"from": account})
    tx.wait(1)
    print("Approved!")
    return tx


def get_lending_pool():
    # ABI
    # Address
    lending_pool_addresses_provider = interface.ILendingPoolAddressesProvider(
        config["networks"][network.show_active()]["lending_pool_addresses_provider"]
    )
    lending_pool_address = lending_pool_addresses_provider.getLendingPool()
    lending_pool = interface.ILendingPool(lending_pool_address)
    return lending_pool


def main():
    account = get_account()
    erc20_address = config["networks"][network.show_active()]["weth_token"]

    # call get_weth() if I don't have WETH yet, or if I'm in my fork environmment
    # get_weth()
    if network.show_active() in ["mainnet-fork", "mainnet-fork-dev"]:
        get_weth()
    # ABI
    # Address
    lending_pool = get_lending_pool()
    # Approve sending out ERC20 tokens
    approve_erc20_token(amount, lending_pool.address, erc20_address, account)
    print("Depositing")
    # function deposit(address asset, uint256 amount, address onBehalfOf, uint16 referralCode)
    tx = lending_pool.deposit(
        erc20_address, amount, account.address, 0, {"from": account}
    )
    tx.wait(1)
    print("Deposited!")
    borrowable_eth, total_debt = get_borrowable_data(lending_pool, account)
    print("Let's borrow")
    # DAI in terms of ETH
    dai_eth_price = get_asset_price(
        config["networks"][network.show_active()]["dai_eth_price_feed"]
    )
    # On multiplie par 0.95 par sécurité, pour être un peu en dessous de la limite de liquidation
    amount_dai_to_borrow = (1 / dai_eth_price) * borrowable_eth * 0.95
    # borowable_eth => borrowable_dai * 0.95
    print(f"We are going to borrow {amount_dai_to_borrow} DAI")
    # Now we will borrow :
    # address asset, uint256 amount, uint256 interestRateMode, uint16 referralCode, address onBehalfOf
    dai_address = config["networks"][network.show_active()]["dai_token"]
    borrow_tx = lending_pool.borrow(
        dai_address,
        Web3.toWei(amount_dai_to_borrow, "ether"),
        1,
        0,
        account.address,
        {"from": account},
    )

    borrow_tx.wait(1)
    print("We should have borrowed some DAI")
    get_borrowable_data(lending_pool, account)
    # repay_all(amount, lending_pool, account)
    print(
        "You just deposited, borrowed, and repayed with Aave, Brownie, and Chainlink!"
    )
