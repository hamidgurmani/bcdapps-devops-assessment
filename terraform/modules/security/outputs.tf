output "alb_security_group_id" {
  description = "Security group ID for the public application load balancer"
  value       = aws_security_group.alb.id
}

output "database_security_group_id" {
  description = "Security group ID for PostgreSQL"
  value       = aws_security_group.database.id
}

output "redis_security_group_id" {
  description = "Security group ID for Redis"
  value       = aws_security_group.redis.id
}
