output "vpc_id" {
  description = "Development VPC ID"
  value       = module.network.vpc_id
}

output "public_subnet_ids" {
  description = "Development public subnet IDs"
  value       = module.network.public_subnet_ids
}

output "private_subnet_ids" {
  description = "Development private subnet IDs"
  value       = module.network.private_subnet_ids
}

output "eks_cluster_name" {
  description = "Development EKS cluster name"
  value       = module.eks.cluster_name
}

output "eks_cluster_endpoint" {
  description = "Private EKS API endpoint"
  value       = module.eks.cluster_endpoint
}

output "postgres_endpoint" {
  description = "Development PostgreSQL endpoint"
  value       = module.database.db_endpoint
}

output "redis_primary_endpoint" {
  description = "Development Redis primary endpoint"
  value       = module.redis.primary_endpoint_address
}

output "alb_security_group_id" {
  description = "Security group reserved for the application load balancer"
  value       = module.security.alb_security_group_id
}
