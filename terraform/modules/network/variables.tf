variable "name" {
  description = "Name prefix for network resources"
  type        = string
}

variable "vpc_cidr" {
  description = "CIDR range for the VPC"
  type        = string
}

variable "az_count" {
  description = "Number of Availability Zones"
  type        = number
  default     = 2

  validation {
    condition     = var.az_count >= 2 && var.az_count <= 3
    error_message = "Use between 2 and 3 Availability Zones."
  }
}

variable "single_nat_gateway" {
  description = "Use one shared NAT Gateway instead of one per AZ"
  type        = bool
  default     = true
}
