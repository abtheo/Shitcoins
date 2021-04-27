
const config = require('./config.json');
const pancakeswap_abi = require('./pancakeswap_abi.json');
const Web3 = require('web3');
const Transaction = require('@ethereumjs/tx').Transaction;
import Common from '@ethereumjs/common';
//Connect to BSC node
const web3 = new Web3('wss://silent-old-pine.bsc.quiknode.pro/50d141387da957f5bd76a5018ec2fd33a7c48dfe/');

//Read wallet private key
const account = web3.eth.accounts.privateKeyToAccount(config.PRIVATE_KEY);
console.log(account);

// Fixed-point notation for number of MFIL which is divisible to 3 decimal places
function financialMfil(numMfil : any) {
    return (Number.parseFloat(numMfil) / 1000).toFixed(3);
}

// Create an async function so I can use the "await" keyword to wait for things to finish
const main = async () => {
    // This code was written and tested using web3 version 1.0.0-beta.29
    console.log(`web3 version: ${web3.version}`)
    
    // Determine the nonce
    var count = await web3.eth.getTransactionCount(account.address);
    console.log(`num transactions so far: ${count}`);
    
    // Pancakeswap Router Address
    var contractAddress = "0x10ED43C718714eb63d5aA57B78B54704E256024E";
    var contract = new web3.eth.Contract(pancakeswap_abi, contractAddress, {
        from: account.address

    });
    // How many tokens do I have before sending?
    var balance = await web3.eth.getBalance(account.address);
    console.log(`Balance before send: ${balance} Gwei BNB\n------------------------`);

    //Construct ABI data ---
    //Swapping BNB for Cosmos(ATOM)
    // Function: swapExactETHForTokens(uint256 amountOutMin, address[] path, address to, uint256 deadline)
    // #	Name	        Type	    Data
    // 0	amountOutMin	uint256	    213549452714469248
    // 1	path	        address[]   [bb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c, == BNB Token Address
    //                                   0eb3a705fc54725037cc9e008bdede697f62f335] == ATOM Token Address
    // 2	to	address	dac3a1b1e64ac9fd73e70fd7887d57d745de795b
    // 3	deadline	uint256	1619471962
    
    const fromToken = "0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c"; //== BNB Token Address
    const toToken = "0x0eb3a705fc54725037cc9e008bdede697f62f335"; //== ATOM Token Address

    const transferAmount = web3.utils.toWei("0.01"); //Swap 0.01BNB

    //Find the expected output amount of the destination token
    const amountsOut = await contract.methods.getAmountsOut(transferAmount, [fromToken, toToken]).call(); 
    const SLIPPAGE_MAX = 5;
    const amountOutMin = web3.utils.toBN(amountsOut[1]).mul(web3.utils.toBN(100 - SLIPPAGE_MAX)).div(web3.utils.toBN(100));
    console.log(`Swapping ${web3.utils.fromWei(transferAmount)} BNB for ATOM`)
    console.log(`Minimum tokens recieved: ${web3.utils.fromWei(amountOutMin.toString())} ATOM`);

    //Arbitrary deadline, can tighten to reject txs if we fail to front-run?
    const minutesDeadline = 5;
    var deadline = new Date( Date.now() + 1000 * (60 * minutesDeadline) ).valueOf() //5 minute deadline
    const swap_abi = contract.methods.swapExactETHForTokens(amountOutMin, [fromToken, toToken], account.address, deadline).encodeABI();

    // Use Gwei for the unit of gas price
    var gasPriceGwei = 5;
    var gasLimit = 3000000;
    // // Chain ID of Binance Smart Chain mainnet
    var chainId = "0x38";

    //Fill in ABI & remaining transaction details
    var rawTransaction = {
        "from": account.address,
        "nonce": "0x" + count.toString(16),
        "gasPrice": web3.utils.toHex(gasPriceGwei * 1e9),
        "gasLimit": web3.utils.toHex(gasLimit),
        "to": contractAddress,
        "data": swap_abi,
        "chainId": chainId,
        "value" : web3.utils.toHex(transferAmount)
    };
    console.log(`Raw of Transaction: \n${JSON.stringify(rawTransaction, null, '\t')}\n------------------------`);
    var signedTx = await web3.eth.accounts.signTransaction(rawTransaction, config.PRIVATE_KEY);
    console.log(signedTx);

    /*
    DANGER -- ACTUALLY EXECUTE THE SWAP
    */

    // var receipt = await web3.eth.sendSignedTransaction(signedTx.rawTransaction);
    // The receipt info of transaction, Uncomment for debug
    // console.log(`Receipt info: \n${JSON.stringify(receipt, null, '\t')}\n------------------------`);

    // // The balance may not be updated yet, but let's check
    var balance = await web3.eth.getBalance(account.address);
    console.log(`Balance after send: ${balance} Gwei BNB\n------------------------`);
    return;
}
main();