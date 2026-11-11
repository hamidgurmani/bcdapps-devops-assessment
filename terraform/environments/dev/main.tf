module "network" {
  source = "../../modules/network"

  name               = "rideflow-dev"
  vpc_cidr           = var.vpc_cidr
  az_count           = 2
  single_nat_gateway = true
}

module "eks" {
  source = "../../modules/eks"

  cluster_name       = "rideflow-dev"
  cluster_version    = var.cluster_version
  private_subnet_ids = module.network.private_subnet_ids

  node_instance_types = ["t3.medium"]
  desired_size        = 1
  min_size            = 1
  max_size            = 2
}

module "security" {
  source = "../../modules/security"

  name                          = "rideflow-dev"
  vpc_id                        = module.network.vpc_id
  eks_cluster_security_group_id = module.eks.cluster_security_group_id
  allowed_ingress_cidrs         = var.allowed_ingress_cidrs
}

module "database" {
  source = "../../modules/database"

  identifier            = "rideflow-dev-postgres"
  database_name         = "rideflow"
  master_username       = "rideflow_admin"
  engine_version        = "16.4"
  instance_class        = "db.t3.micro"
  allocated_storage     = 20
  max_allocated_storage = 50
  subnet_ids            = module.network.private_subnet_ids
  security_group_ids    = [module.security.database_security_group_id]

  backup_retention_period = 7
  multi_az                = false
  deletion_protection     = false
}

module "redis" {
  source = "../../modules/redis"

  replication_group_id = "rideflow-dev-redis"
  description          = "RideFlow development Redis cache"
  node_type            = "cache.t3.micro"
  engine_version       = "7.1"
  num_cache_clusters   = 1
  subnet_ids           = module.network.private_subnet_ids
  security_group_ids   = [module.security.redis_security_group_id]
  auth_token           = var.redis_auth_token
}
