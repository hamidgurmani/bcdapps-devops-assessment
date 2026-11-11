module "network" {
  source = "../../modules/network"

  name               = "rideflow-prod"
  vpc_cidr           = var.vpc_cidr
  az_count           = 2
  single_nat_gateway = false
}

module "eks" {
  source = "../../modules/eks"

  cluster_name       = "rideflow-prod"
  cluster_version    = var.cluster_version
  private_subnet_ids = module.network.private_subnet_ids

  node_instance_types = ["t3.medium"]
  desired_size        = 2
  min_size            = 2
  max_size            = 3
}

module "security" {
  source = "../../modules/security"

  name                          = "rideflow-prod"
  vpc_id                        = module.network.vpc_id
  eks_cluster_security_group_id = module.eks.cluster_security_group_id
  allowed_ingress_cidrs         = var.allowed_ingress_cidrs
}

module "database" {
  source = "../../modules/database"

  identifier            = "rideflow-prod-postgres"
  database_name         = "rideflow"
  master_username       = "rideflow_admin"
  engine_version        = "16.4"
  instance_class        = "db.t3.small"
  allocated_storage     = 50
  max_allocated_storage = 200
  subnet_ids            = module.network.private_subnet_ids
  security_group_ids    = [module.security.database_security_group_id]

  backup_retention_period = 14
  multi_az                = true
  deletion_protection     = true
}

module "redis" {
  source = "../../modules/redis"

  replication_group_id = "rideflow-prod-redis"
  description          = "RideFlow production Redis cache"
  node_type            = "cache.t3.small"
  engine_version       = "7.1"
  num_cache_clusters   = 2
  subnet_ids           = module.network.private_subnet_ids
  security_group_ids   = [module.security.redis_security_group_id]
  auth_token           = var.redis_auth_token
}
