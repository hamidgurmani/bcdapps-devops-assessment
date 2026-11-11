variable "identifier" {
  description = "Unique RDS instance identifier"
  type        = string
}

variable "database_name" {
  description = "Initial PostgreSQL database name"
  type        = string
}

variable "master_username" {
  description = "PostgreSQL master username"
  type        = string
}

variable "engine_version" {
  description = "PostgreSQL engine version supported by AWS RDS"
  type        = string
}

variable "instance_class" {
  description = "RDS instance class"
  type        = string
}

variable "allocated_storage" {
  description = "Initial storage allocation in GiB"
  type        = number
  default     = 20
}

variable "max_allocated_storage" {
  description = "Maximum autoscaled storage in GiB"
  type        = number
  default     = 100
}

variable "subnet_ids" {
  description = "Private subnet IDs for RDS"
  type        = list(string)
}

variable "security_group_ids" {
  description = "Security groups controlling database access"
  type        = list(string)
}

variable "backup_retention_period" {
  description = "Automated backup retention in days"
  type        = number
  default     = 7
}

variable "multi_az" {
  description = "Enable Multi-AZ deployment"
  type        = bool
  default     = false
}

variable "deletion_protection" {
  description = "Protect the database from accidental deletion"
  type        = bool
  default     = true
}
