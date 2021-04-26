
const config = require('config');
config minefil_abi = require('minefil_abi');
const Web3 = require('web3');
const Tx = require('ethereumjs-tx');

//Read wallet private key
const account = web3.eth.accounts.privateKeyToAccount(config.PRIVATE_KEY)

//Connect to BSC node
const web3 = new Web3('wss://silent-old-pine.bsc.quiknode.pro/50d141387da957f5bd76a5018ec2fd33a7c48dfe/');

// Fixed-point notation for number of MFIL which is divisible to 3 decimal places
function financialMfil(numMfil) {
    return Number.parseFloat(numMfil / 1e3).toFixed(3);
}
// Create an async function so I can use the "await" keyword to wait for things to finish
const main = async () => {
    // This code was written and tested using web3 version 1.0.0-beta.29
    console.log(`web3 version: ${web3.version}`)
    // Who holds the token now?
    var myAddress = "0x644dE7C3f6425D8920332FC6C97Fbf7e04445C74";
    // Who are we trying to send this token to?
    var destAddress = "0xE3A029F6cA0C32a9E6c9a2154790Ea0A92cb2621";
    // MineFIL Token (MFIL) is divisible to 3 decimal places, 1 = 0.001 of MFIL
    var transferAmount = 1;
    // Determine the nonce
    var count = await web3.eth.getTransactionCount(myAddress);
    console.log(`num transactions so far: ${count}`);
    // MineFILToekn contract ABI Array

    
    // The address of the contract which created MFIL
    var contractAddress = "0x1564A92a0870aF0eBf1F015f5FD223abaA3505CA";
    var contract = new web3.eth.Contract(abiArray, contractAddress, {
        from: myAddress
    });
    // How many tokens do I have before sending?
    var balance = await contract.methods.balanceOf(myAddress).call();
    console.log(`Balance before send: ${financialMfil(balance)} MFIL\n------------------------`);
    // I chose gas price and gas limit based on what ethereum wallet was recommending for a similar transaction. You may need to change the gas price!
    // Use Gwei for the unit of gas price
    var gasPriceGwei = 3;
    var gasLimit = 3000000;
    // Chain ID of Ropsten Test Net is 3, replace it to 1 for Main Net
    var chainId = 3;
    var rawTransaction = {
        "from": myAddress,
        "nonce": "0x" + count.toString(16),
        "gasPrice": web3.utils.toHex(gasPriceGwei * 1e9),
        "gasLimit": web3.utils.toHex(gasLimit),
        "to": contractAddress,
        "value": "0x0",
        "data": contract.methods.transfer(destAddress, transferAmount).encodeABI(),
        "chainId": chainId
    };
    console.log(`Raw of Transaction: \n${JSON.stringify(rawTransaction, null, '\t')}\n------------------------`);
    // The private key for myAddress in .env
    var privKey = new Buffer(process.env["PRIVATE_KEY"], 'hex');
    var tx = new Tx(rawTransaction);
    tx.sign(privKey);
    var serializedTx = tx.serialize();
    // Comment out these four lines if you don't really want to send the TX right now
    console.log(`Attempting to send signed tx:  ${serializedTx.toString('hex')}\n------------------------`);
    var receipt = await web3.eth.sendSignedTransaction('0x' + serializedTx.toString('hex'));
    // The receipt info of transaction, Uncomment for debug
    console.log(`Receipt info: \n${JSON.stringify(receipt, null, '\t')}\n------------------------`);
    // The balance may not be updated yet, but let's check
    balance = await contract.methods.balanceOf(myAddress).call();
    console.log(`Balance after send: ${financialMfil(balance)} MFIL`);
}
main();