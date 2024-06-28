from web3 import AsyncWeb3, Web3


def ether_to_usdt(eth):
    return eth * 3581.9


def usdt_to_rub(usdt):
    return usdt * 90


async def check_balance(wallet_addr):
    binance_testnet_rpc_url = "https://ethereum-rpc.publicnode.com"
    web3 = Web3(Web3.HTTPProvider(binance_testnet_rpc_url))
    if web3.is_connected():
        checksum_address = web3.to_checksum_address(wallet_addr)
        wei_balance = web3.eth.get_balance(checksum_address)
        eth_balance = web3.from_wei(wei_balance, "ether")
        return usdt_to_rub(round(ether_to_usdt(float(eth_balance)), 4))
