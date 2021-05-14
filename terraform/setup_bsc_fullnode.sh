#! /bin/bash
sudo yum install go -y
sudo yum install git -y

#Install Python deps
sudo yum install libxslt-devel libxml2-devel python3-devel -y


sudo git clone https://github.com/binance-chain/bsc
# Enter the folder bsc was cloned into
cd bsc

# Fix checksum mismatch issue
sudo rm go.sum
sudo go mod tidy

# Compile and install bsc
sudo make geth

## mainet
sudo wget   $(curl -s https://api.github.com/repos/binance-chain/bsc/releases/latest |grep browser_ |grep mainnet |cut -d\" -f4)
sudo unzip -o mainnet.zip

# Write genesis state locally, and start the fullnode
sudo ./build/bin/geth --datadir node init genesis.json
sudo ./build/bin/geth --config ./config.toml --datadir ./node --nousb --ws --cache 24576 --syncmode "fast"

sudo echo "Setup successful" > success.txt
