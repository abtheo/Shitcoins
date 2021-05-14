
from web3 import Web3
from threading import Thread
import time
import json
import os
import sys

filepath = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
pancakefile = filepath + "/pancakeswap_abi.json"
with open(pancakefile) as f:
    pancakeswap_abi = json.load(f)


def try_decode_input(tx):
    try:
        input_raw = tx["input"]
        return contract.decode_function_input(input_raw)
    except:
        return None


def try_get_tx(tx):
    try:
        w3.eth.getTransaction(tx)
    except:
        return None

ip = sys.argv[1]
# Connect to BSC node

w3 = Web3(Web3.WebsocketProvider(
    'wss://' + ip + ':8546'))


# Pancakeswap Router Address
contractAddress = "0x000000000000000000000000000000000000dEaD"
contract = w3.eth.contract(address=contractAddress, abi=pancakeswap_abi)
print(contract)

block_filter = w3.eth.filter('pending')
# block_filter = contract.events.removeLiquidityETHWithPermit.createFilter(
#     fromBlock='pending')
print (block_filter)

for i in range(20):
    pending_tx_hashes = block_filter.get_new_entries()
    print(pending_tx_hashes)

    transactions = [try_get_tx(h) for h in pending_tx_hashes]

    tx_inputs = [try_decode_input(tx)
                 for tx in transactions]
    print(tx_inputs)

    remove_lp = ["removeLiquidityETHWithPermit" in tx_inputs]

    if any(remove_lp):
        print(tx_inputs)
        break

    time.sleep(0.5)

# print(transactions)
# print(tx_inputs)
# Could fail for transactions which are not yet allocated to a block


# print(transactions[0])
# print(transactions)

# gas = [int(tx["gas"]) for tx in transactions]
# print(gas)
# def handle_event(event):
#     print(event)

#     # transactions = [web3.eth.getTransaction(h) for h in transaction_hashes]
#     # and whatever


# def log_loop(event_filter, poll_interval):
#     while True:
#         for event in event_filter.get_new_entries():
#             handle_event(event)
#         time.sleep(poll_interval)


# def main():

#     block_filter = w3.eth.filter('pending')
#     worker = Thread(target=log_loop, args=(block_filter, 5), daemon=True)
#     worker.start()
#     # .. do some other stuff


# if __name__ == '__main__':
#     main()
