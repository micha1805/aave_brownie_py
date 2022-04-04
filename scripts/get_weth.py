from scripts.helpful_scripts import get_account
from brownie import interface, config, network


def get_weth():
    """
    Mints WETH by depositing ETH
    """
    # Needed :
    # - ABI
    # - Address
    account = get_account()
    weth = interface.IWeth(config["networks"][network.show_active()]["weth_token"])
    # ici on appelle juste la fonction deposit du contrat, qu'on peut faire aussi
    # en ligne sur etherscan dans "Write Contract"
    amount_of_weth_desired = 0.1
    tx = weth.deposit({"from": account, "value": amount_of_weth_desired * 10 ** 18})
    tx.wait(1)
    print(f"Received {amount_of_weth_desired} WETH (normally...)")
    return tx


def main():
    get_weth()
