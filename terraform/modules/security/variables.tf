variable "name" {
  description = "Environment name prefix"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID where security groups will be created"
  type        = string
}

variable "eks_cluster_security_group_id" {
  description = "EKS cluster security group allowed to access private data services"
  type        = string
}

variable "allowed_ingress_cidrs" {
  description = "CIDR ranges permitted to access the public load balancer"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}
