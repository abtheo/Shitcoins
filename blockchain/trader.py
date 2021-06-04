from web3 import Web3
from eth_account import Account
import json
import datetime
from time import sleep
import os
import numpy as np

class Trader:
    def __init__(self):
        # Load config files
        filepath = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        configFile = filepath + "/config.json"
        pancakeABI = filepath + "/pancakeswap_abi.json"
        erc20ABI = filepath + "/erc20.json"
        factoryABI = filepath + "/factory.json"

        with open(configFile) as f:
            self.config = json.load(f)
        with open(pancakeABI) as f:
            self.pancakeswap_abi = json.load(f)
        with open(erc20ABI) as f:
            self.erc20_abi = json.load(f)
        with open(factoryABI) as f:
            self.factory_abi = json.load(f)

        self.balance_check_abi = json.loads('[{"constant":true,"inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"balance","type":"uint256"}],"payable":false,"type":"function"}]')

        # Connect to BSC node
        self.w3 = Web3(Web3.WebsocketProvider(
            'wss://silent-old-pine.bsc.quiknode.pro/'))

        # Pancakeswap Router Contract
        self.pancakeswapAddress = "0x10ED43C718714eb63d5aA57B78B54704E256024E"
        self.pancake_contract = self.w3.eth.contract(
            address=self.pancakeswapAddress, abi=self.pancakeswap_abi)

        #Pancakeswap Factory Contract
        self.factory_contract = self.w3.eth.contract(
            address="0xcA143Ce32Fe78f1f7019d7d551a6402fC5350c73",
            abi=self.factory_abi
        )

        # Read wallet private key
        self.account = Account.from_key(self.config["PRIVATE_KEY"])

        # Chain ID of Binance Smart Chain mainnet
        self.chainId = "0x38"

        self.bnb_address = Web3.toChecksumAddress(
            "0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c")
        self.gasLimit = 5000000

    def swapExactETHForTokens(self, toTokenAddress, transferAmountInBNB, gasPriceGwei=8, max_slippage=5, minutesDeadline=5, actually_send_trade=False, retries=1, verbose=False):
        # Convert BNB to BNB-Wei
        transferAmount = Web3.toWei(transferAmountInBNB, "ether")
        # Ensure address is properly formatted
        toToken = Web3.toChecksumAddress(toTokenAddress)

        # Determine the nonce
        count = self.w3.eth.getTransactionCount(self.account.address)
        if verbose:
            print("Nonce: ", count)

        # Get BNB balance
        balance = self.w3.eth.getBalance(self.account.address)
        if verbose:
            print(
                f"Balance before send: {balance} Gwei BNB\n------------------------")

        if balance < transferAmount:
            raise Exception(
                "Requested swap value is greater than the account balance. Will not execute this trade.")

        # Find the expected output amount of the destination token
        amountsOut = self.pancake_contract.functions.getAmountsOut(
            transferAmount, [self.bnb_address, toToken]).call()
        # amountOutMin = amountsOut[1] * (100 - max_slippage) / 100
        amountOutMin = 1

        # Arbitrary deadline, can tighten to reject txs if we fail to front-run?
        deadline = datetime.datetime.now(
            datetime.timezone.utc).timestamp() + (minutesDeadline * 60)

        # Fill ABI data payload with parameters:
        # swapExactETHForTokens(uint256 amountOutMin, address[] path, address to, uint256 deadline)
        swap_abi = self.pancake_contract.encodeABI('swapExactETHForTokens',
                                                   args=[int(amountOutMin), [self.bnb_address, toToken], self.account.address, int(deadline)])

        # Fill in ABI & remaining transaction details
        rawTransaction = {
            "from": self.account.address,
            "to": self.pancakeswapAddress,
            "nonce": Web3.toHex(count),
            "gasPrice": Web3.toHex(int(gasPriceGwei * 1e9)),
            "gas": Web3.toHex(self.gasLimit),
            "data": swap_abi,
            "chainId": self.chainId,
            "value": Web3.toHex(transferAmount)
        }

        if verbose:
            print(
                f"Raw of Transaction: \n${rawTransaction}\n------------------------")

        signedTx = self.w3.eth.account.sign_transaction(
            rawTransaction, self.config["PRIVATE_KEY"])

        """
        <DANGER -- ACTUALLY EXECUTE THE SWAP>
        """
        if actually_send_trade:
            for i in range(retries):
                try:
                    deploy_txn = self.w3.eth.send_raw_transaction(
                        signedTx.rawTransaction)
                    txn_receipt = self.w3.eth.wait_for_transaction_receipt(deploy_txn)
                    if verbose:
                        print(txn_receipt)
                    
                    #Check status of txn_receipt
                    
                    
                    return txn_receipt

                except Exception as e:
                    print(e)
                    print(f"Failed on attempt {i}/{retries}")
        """
            </DANGER>
        """

        return "Failed"

    def swapExactTokensForETH(self,fromTokenAddress, gasPriceGwei=8, transferAmountPercentage=1.0, retries=1, minutesDeadline=5, max_slippage=5, verbose=False,actually_send_trade=False):
        # Ensure address is properly formatted
        fromToken = Web3.toChecksumAddress(fromTokenAddress)

        # Get fromToken balance
        balance_check_contract = self.w3.eth.contract(
            address=fromToken, abi=self.balance_check_abi)

        balance = balance_check_contract.functions.balanceOf(self.account.address).call({'from':fromToken})

        if verbose:
            print(
                f"Balance before send: {balance} Wei Shitcoin\n------------------------")

        # Determine percentage of position to exit
        # transferAmount = int(np.float64(transferAmountPercentage) * np.int64(balance))
        transferAmount = balance
        if balance < transferAmount:
            raise Exception(
                "Requested swap value is greater than the account balance. Will not execute this trade.")

        # Find the expected output amount of the destination token
        amountsOut = self.pancake_contract.functions.getAmountsOut(
            transferAmount, [fromToken, self.bnb_address]).call()
        # amountOutMin = amountsOut[1] * (100 - max_slippage) / 100
        amountOutMin = 1
        if verbose:
            print(
                f"Minimum amount out: {amountOutMin} Wei BNB\n------------------------")

        # Arbitrary deadline, can tighten to reject txs if we fail to front-run?
        deadline = datetime.datetime.now(
            datetime.timezone.utc).timestamp() + (minutesDeadline * 60)

        # Fill ABI data payload with parameters:
        # swapExactTokensForETH(uint256 amountIn, uint256 amountOutMin, address[] path, address to, uint256 deadline)
        swap_abi = self.pancake_contract.encodeABI('swapExactTokensForETH',
                                                   args=[int(transferAmount), int(amountOutMin), [fromToken, self.bnb_address], self.account.address, int(deadline)])

        # Fill in ABI & remaining transaction details
        

        """
        <DANGER -- ACTUALLY EXECUTE THE SWAP>
        """
        if actually_send_trade:
            #Approve shitcoin trade
            max_approval_hex = f"0x{64 * 'f'}"
            max_approval_int = int(max_approval_hex, 16)

            token_contract = self.w3.eth.contract(
                address=fromToken, abi=self.erc20_abi)

            approve_function = token_contract.functions.approve(self.pancakeswapAddress, max_approval_int)

            approveTransaction = {
                "from": self.account.address,
                "nonce": Web3.toHex(self.w3.eth.getTransactionCount(self.account.address)),
                "gasPrice": Web3.toHex(int(gasPriceGwei * 1e9)),
                "gas": Web3.toHex(self.gasLimit),
                "chainId": self.chainId
            }
            
            approvalTx = approve_function.buildTransaction(approveTransaction)

            signedApprovalTx = self.w3.eth.account.sign_transaction(
                approvalTx, self.config["PRIVATE_KEY"])

            
            approved = False
            for i in range(retries):
                try:   
                    if not approved:
                        approval_tx = self.w3.eth.send_raw_transaction(
                            signedApprovalTx.rawTransaction)
                        approval_txn_receipt = self.w3.eth.wait_for_transaction_receipt(approval_tx,timeout=240)

                        if verbose:
                            print(approval_txn_receipt)
                    approved = True

                    rawTransaction = {
                        "from": self.account.address,
                        "to": self.pancakeswapAddress,
                        "nonce": Web3.toHex(self.w3.eth.getTransactionCount(self.account.address)),
                        "gasPrice": Web3.toHex(int(gasPriceGwei * 1e9)),
                        "gas": Web3.toHex(self.gasLimit),
                        "data": swap_abi,
                        "chainId": self.chainId,
                        "value": "0x0"
                    }

                    if verbose:
                        print(
                            f"Raw of Transaction: \n${rawTransaction}\n------------------------")

                    signedTx = self.w3.eth.account.sign_transaction(
                        rawTransaction, self.config["PRIVATE_KEY"])

                    deploy_txn = self.w3.eth.send_raw_transaction(
                        signedTx.rawTransaction)
                    txn_receipt = self.w3.eth.wait_for_transaction_receipt(deploy_txn,timeout=240)
                    if verbose:
                        print(txn_receipt)
                    
                    return txn_receipt

                except Exception as e:
                    print(e)
                    print(f"Failed on attempt {i}/{retries}")
            """
            </DANGER>
        """

        return "Failed"

    def get_shitcoin_price_in_bnb(self, shitcoinAddress, bnb_value=1, convertToBNB=True):
        # Ensure address is properly formatted
        fromToken = Web3.toChecksumAddress(shitcoinAddress)
        # Find the expected output amount of the destination token
        amountsOut = self.pancake_contract.functions.getAmountsOut(
            Web3.toWei(bnb_value, 'ether'), [fromToken, self.bnb_address]).call()[1]

        if convertToBNB:
            return np.divide(1,Web3.fromWei(amountsOut, 'ether'))
        return np.divide(1,amountsOut)
    
    def get_bnb_balance(self,convertToBNB=True):
        balance = self.w3.eth.getBalance(self.account.address)
        if convertToBNB:
            return Web3.fromWei(balance, 'ether')
        return balance

    def get_shitcoin_balance(self,shitcoinAddress,convertToBNB=True):
        # Ensure address is properly formatted
        fromToken = Web3.toChecksumAddress(shitcoinAddress)

        balance_check_contract = self.w3.eth.contract(
            address=fromToken, abi=self.balance_check_abi)

        balance = balance_check_contract.functions.balanceOf(self.account.address).call({'from':fromToken})
        
        if convertToBNB:
            return Web3.fromWei(balance, 'ether')
        return balance
