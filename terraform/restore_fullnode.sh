#! /bin/bash
sudo yum install go -y
sudo yum install git -y

#Install Python deps
sudo yum install libxslt-devel libxml2-devel python3-devel -y

# Mount the EBS volume containing the BSC chain and GETH stuff
sudo mkdir /mnt/ebs/
sudo mount -t ext4 /dev/sdh /mnt/ebs/

# Install GETH etc
cd /
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

# Fix bug that stops geth from working
sudo sed -i 's/WSModules = ["net", "web3", "eth"]/WSModules = ["net", "txpool", "web3", "eth"]/g' config.toml
sudo sed -i 's/GraphQLPort = 8557/#GraphQLPort = 8557/g' config.toml

# start the fullnode
sudo ./build/bin/geth --config ./config.toml --datadir /mnt/ebs/bsc/node --nousb --ws --syncmode "fast"
