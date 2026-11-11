variable "replication_group_id" {
  description = "Unique ElastiCache replication group identifier"
  type        = string
}

variable "description" {
  description = "Description of the Redis replication group"
  type        = string
  default     = "RideFlow Redis cache"
}

variable "node_type" {
  description = "ElastiCache node instance type"
  type        = string
}

variable "engine_version" {
  description = "Redis engine version"
  type        = string
}

variable "num_cache_clusters" {
  description = "Number of cache nodes including the primary"
  type        = number
  default     = 2
}

variable "subnet_ids" {
  description = "Private subnet IDs for Redis"
  type        = list(string)
}

variable "security_group_ids" {
  description = "Security groups controlling Redis access"
  type        = list(string)
}

variable "auth_token" {
  description = "Redis AUTH token supplied securely at deployment"
  type        = string
  sensitive   = true
}
