
from web3 import Web3
from eth_account import Account
import json
import datetime


# Load config files
with open('./config.json') as f:
    config = json.load(f)


with open('./pancakeswap_abi.json') as f:
    pancakeswap_abi = json.load(f)

# Connect to BSC node
web3 = Web3(Web3.WebsocketProvider(
    'wss://silent-old-pine.bsc.quiknode.pro/50d141387da957f5bd76a5018ec2fd33a7c48dfe/'))

# Read wallet private key
account = Account.from_key(config["PRIVATE_KEY"])
print(account)

# Determine the nonce
count = web3.eth.getTransactionCount(account.address)
print("Nonce: ", count)

# Pancakeswap Router Address
contractAddress = "0x10ED43C718714eb63d5aA57B78B54704E256024E"
contract = web3.eth.contract(address=contractAddress, abi=pancakeswap_abi)

# How many tokens do I have before sending?
balance = web3.eth.getBalance(account.address)
print(f"Balance before send: {balance} Gwei BNB\n------------------------")

# Construct ABI data ---
# Swapping BNB for Cosmos(ATOM)
# Function: swapExactETHForTokens(uint256 amountOutMin, address[] path, address to, uint256 deadline)
# #	Name	        Type	    Data
# 0	amountOutMin	uint256	    213549452714469248
# 1	path	        address[]   [bb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c, == BNB Token Address
#                                   0eb3a705fc54725037cc9e008bdede697f62f335] == ATOM Token Address
# 2	to	address	dac3a1b1e64ac9fd73e70fd7887d57d745de795b
# 3	deadline	uint256	1619471962

fromToken = Web3.toChecksumAddress(
    "0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c")  # == BNB Token Address
toToken = Web3.toChecksumAddress(
    "0x0eb3a705fc54725037cc9e008bdede697f62f335")  # == ATOM Token Address

transferAmount = Web3.toWei(0.01, "ether")  # Swap 0.01BNB

# Find the expected output amount of the destination token
amountsOut = contract.functions.getAmountsOut(
    transferAmount, [fromToken, toToken]).call()

SLIPPAGE_MAX = 5
amountOutMin = amountsOut[1] * (100 - SLIPPAGE_MAX) / 100
print(f"Swapping {Web3.fromWei(transferAmount,'ether')} BNB for ATOM")
print(f"Minimum tokens recieved: {Web3.fromWei(amountOutMin,'ether')} ATOM")

# Arbitrary deadline, can tighten to reject txs if we fail to front-run?
minutesDeadline = 5
deadline = datetime.datetime.now(
    datetime.timezone.utc).timestamp() + (minutesDeadline * 60)

# Fill ABI data payload with parameters
swap_abi = contract.encodeABI('swapExactETHForTokens',
                              args=[int(amountOutMin), [fromToken, toToken], account.address, int(deadline)])

# Use Gwei for the unit of gas price
gasPriceGwei = 5
gasLimit = 3000000
# # Chain ID of Binance Smart Chain mainnet
chainId = "0x38"

# Fill in ABI & remaining transaction details
rawTransaction = {
    "from": account.address,
    "nonce": web3.toHex(count),
    "gasPrice": Web3.toHex(int(gasPriceGwei * 1e9)),
    "gas": Web3.toHex(gasLimit),
    "to": contractAddress,
    "data": swap_abi,
    "chainId": chainId,
    "value": Web3.toHex(transferAmount)
}
print(f"Raw of Transaction: \n${rawTransaction}\n------------------------")
signedTx = web3.eth.account.sign_transaction(
    rawTransaction, config["PRIVATE_KEY"])
print(signedTx)

"""
    <DANGER -- ACTUALLY EXECUTE THE SWAP>
"""
# deploy_txn = web3.eth.send_raw_transaction(signedTx.rawTransaction)
"""
    </DANGER>
"""
txn_receipt = web3.eth.wait_for_transaction_receipt(deploy_txn)
print(txn_receipt)

# The balance may not be updated yet, but let's check
balance = web3.eth.getBalance(account.address)
print(f"Balance after send: {balance} Gwei BNB\n------------------------")
