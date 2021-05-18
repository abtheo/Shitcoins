terraform {
  backend "s3" {
    bucket = "shitcoin-tf-state-bucket"
    key = "terraform/shitcoins.tfstate"
    region = "us-west-2"
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.27"
    }
  }
  required_version = ">= 0.14.9"
}

provider "aws" {
  profile = "default"
  region  = "us-west-2"
}

module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "2.21.0"
  # insert the 8 required variables here

  name = var.vpc_name
  cidr = var.vpc_cidr

  azs             = var.vpc_azs
  public_subnets = var.vpc_public_subnets
}

resource "aws_security_group_rule" "allow_wss" {
  type              = "ingress"
  from_port         = 0
  to_port           = 0
  protocol          = "tcp"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = module.bsc_node_sg.security_group_id
}

module "bsc_node_sg" {
  source  = "terraform-aws-modules/security-group/aws"
  version = "4.0.0"

  name = "bsc_node_sg"
  description = "Allows SSH in, and all traffic out"
  vpc_id = module.vpc.vpc_id

  # Use 0/0 for all ingress/egress rules (poor security practice!)
  ingress_cidr_blocks = ["0.0.0.0/0"]
  egress_cidr_blocks = ["0.0.0.0/0"]

  ingress_rules = ["all-all"]
  egress_rules = ["all-all"]
}

resource "aws_key_pair" "node_ssh_key" {
  key_name   = "ssh-key"
  public_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCVQvR6A2iRz9TKC5ROgm3mMT6G04/HL5m/2xl/Wn84/5H+vBomAPl+xN0WHiyj6evSXkBQK0XEZImKk1S3hoBcJz2ms9nQCufCSjHTwzq7totMnND+zaZJlBZsRiSPmQoppvOnlQpIdczpTDQEQ6TndFelLxGvl9N3B3E9Hte8YauZPo3OkD0GOXZp1EyrjgK/n7iG87M1ZJa75+j0MiBFZnhkiipdtpWPO2E4y7Zc76+AXuBxpAPmkiBPtj/ZdzUJDlkZvEDMubtE4huHt0iYgUTXr2K2ihIx+iuG+cIUYrzBNkEduGwbIhZqc0lQLR9bwMCFvFo8eyDBzHApsv3b imported-openssh-key"
}

resource "aws_s3_bucket" "state_bucket" {
  bucket = "shitcoin-tf-state-bucket"
  acl    = "private"
}

resource "aws_ebs_volume" "bsc_disk" {
  availability_zone = module.vpc.azs[0]
  size = 320
  snapshot_id = "snap-0699cdda04ba79e75"
}

module "ec2_instances" {
  source  = "terraform-aws-modules/ec2-instance/aws"
  version = "2.12.0"

  name           = "bsc-node"
  ami                    = "ami-0cf6f5c8a62fa5da6"
  instance_type          = "m5n.large"
  vpc_security_group_ids = [module.bsc_node_sg.security_group_id]
  subnet_id              = module.vpc.public_subnets[0]
  key_name               = aws_key_pair.node_ssh_key.key_name

  user_data = "${file("restore_fullnode.sh")}"
}

resource "aws_volume_attachment" "node_vol_att" {
  device_name = "/dev/sdh"
  volume_id   = aws_ebs_volume.bsc_disk.id
  instance_id = module.ec2_instances.id[0]
}
