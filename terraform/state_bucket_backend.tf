terraform {
    
  required_version = ">= 1.10.0"

  backend "s3" {
    bucket         = "fysh-state-bucket" # Same as above
    key            = "global/s3/terraform.tfstate"     # Path within the bucket
    region         = "eu-west-2"
    encrypt        = true
    use_lockfile   = true                              # Enables S3 Native Locking
  }
}