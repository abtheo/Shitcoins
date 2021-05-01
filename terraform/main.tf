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

resource "aws_s3_bucket" "state_bucket" {
  bucket = "shitcoin-tf-state-bucket"
  acl    = "private"
}
