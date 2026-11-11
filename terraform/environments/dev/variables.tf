variable "aws_region" {
  description = "AWS deployment region"
  type        = string
  default     = "us-east-1"
}

variable "vpc_cidr" {
  description = "Development VPC CIDR"
  type        = string
  default     = "10.10.0.0/16"
}

variable "cluster_version" {
  description = "EKS Kubernetes version"
  type        = string
  default     = "1.34"
}

variable "redis_auth_token" {
  description = "Redis AUTH token supplied through TF_VAR_redis_auth_token"
  type        = string
  sensitive   = true
}

variable "allowed_ingress_cidrs" {
  description = "CIDRs permitted to access the application load balancer"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}
