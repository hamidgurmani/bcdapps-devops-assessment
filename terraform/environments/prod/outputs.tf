output "vpc_id" {
  description = "Production VPC ID"
  value       = module.network.vpc_id
}

output "public_subnet_ids" {
  description = "Production public subnet IDs"
  value       = module.network.public_subnet_ids
}

output "private_subnet_ids" {
  description = "Production private subnet IDs"
  value       = module.network.private_subnet_ids
}

output "eks_cluster_name" {
  description = "Production EKS cluster name"
  value       = module.eks.cluster_name
}

output "eks_cluster_endpoint" {
  description = "Private EKS API endpoint"
  value       = module.eks.cluster_endpoint
}

output "postgres_endpoint" {
  description = "Production PostgreSQL endpoint"
  value       = module.database.db_endpoint
}

output "redis_primary_endpoint" {
  description = "Production Redis primary endpoint"
  value       = module.redis.primary_endpoint_address
}

output "redis_reader_endpoint" {
  description = "Production Redis reader endpoint"
  value       = module.redis.reader_endpoint_address
}

output "alb_security_group_id" {
  description = "Security group reserved for the application load balancer"
  value       = module.security.alb_security_group_id
}
