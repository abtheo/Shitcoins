
//Read private key
var config = require('./config.json');
const Web3 = require('web3');


const web3 = new Web3('wss://silent-old-pine.bsc.quiknode.pro/50d141387da957f5bd76a5018ec2fd33a7c48dfe/');

async function main() {
    const account = web3.eth.accounts.privateKeyToAccount(config.PRIVATE_KEY)
    console.log(account);
    // var subscription = web3.eth.subscribe('pendingTransactions', function(error, result){
    //     if (!error)
    //         console.log(result);
    //     console.log(error);
    // })
    // .on("connected", function(subscriptionId){
    //     console.log(subscriptionId);
    // })
    // .on("data", function(log){
    //     console.log(log);
    // })
    // .on("changed", function(log){
    // });

    // unsubscribes the subscription
    // subscription.unsubscribe(function(error, success){
    // if(success)
    //     console.log('Successfully unsubscribed!');
    // if(error)
    //     web3.eth.clearSubscriptions();
    //});
}

main()
web3.eth.clearSubscriptions();