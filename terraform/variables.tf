variable "public_subnets" {
    description = "List of public subnet IDs for the ECS tasks"
    type        = list(string)
    default = [ "subnet-046ec8b4e41d59ea8", "subnet-0cfeaca0e941dea5b", "subnet-055ac264d45bec709" ]
}

variable "vpc_id" {
    description = "The ID of the VPC where the ECS tasks will run"
    type        = string
    default = "vpc-03f0d39570fbaa750"
}

variable "aws_region" {
    description = "The AWS region where resources will be created"
    type        = string
    default     = "eu-west-2"
}