# Shitcoins

To the Moon! 🚀🚀

## Setup

Live trading requires a private key for a BSC wallet.

[How to Export a Private Key from MetaMask](https://metamask.zendesk.com/hc/en-us/articles/360015289632-How-to-Export-an-Account-Private-Key)

To add your private key to the application, create the file `/blockchain/config.json` and complete as follows:
```
{
    "PRIVATE_KEY" : "<YOUR-PRIVATE-KEY>"
}
```

To setup dev tooling:
Install AWS CLI
Install Terraform, and navigate to the project directory
'aws configure'
  Add Access Key ID and Access Key
  Set default region to us-west-2
  Leave default output format as yaml
'terraform init'
