output "db_instance_identifier" {
  description = "RDS instance identifier"
  value       = aws_db_instance.this.identifier
}

output "db_endpoint" {
  description = "RDS endpoint address and port"
  value       = aws_db_instance.this.endpoint
}

output "db_port" {
  description = "PostgreSQL port"
  value       = aws_db_instance.this.port
}

output "db_name" {
  description = "Initial database name"
  value       = aws_db_instance.this.db_name
}

output "master_user_secret_arn" {
  description = "Secrets Manager ARN for the RDS master credentials"
  value       = aws_db_instance.this.master_user_secret[0].secret_arn
}
