# AWS Cost Estimate

## 1. Estimate assumptions

This estimate models the AWS infrastructure defined in the Terraform development and production environments.

- **Region:** US East (N. Virginia), `us-east-1`
- **Billing model:** On-demand pricing, Linux instances
- **Month:** 730 hours
- **Currency:** USD
- **Usage:** Resources run continuously for the full month
- **EKS:** Standard Kubernetes version support at $0.10 per cluster-hour
- **EKS worker nodes:** Baseline desired capacity, not autoscaling maximum
- **Pricing basis:** Approximate public list prices checked on November 12, 2026

This is an estimate, not an actual AWS bill. The Terraform infrastructure has been validated but has not been provisioned in AWS. Actual charges depend on usage, configuration, pricing changes, and applicable taxes.

## 2. Configured infrastructure

| Resource | Development | Production |
|---|---|---|
| Availability Zones | 2 | 2 |
| EKS clusters | 1 | 1 |
| EKS worker instance | 1 x t3.medium | 2 x t3.medium |
| Worker autoscaling | 1-2 nodes | 2-3 nodes |
| NAT Gateways | 1 | 2 |
| RDS engine | PostgreSQL 16.4 | PostgreSQL 16.4 |
| RDS instance | db.t3.micro | db.t3.small |
| RDS allocated storage | 20 GB gp3 | 50 GB gp3 |
| RDS maximum autoscaled storage | 50 GB | 200 GB |
| RDS Multi-AZ | No | Yes |
| RDS backup retention | 7 days | 14 days |
| Redis node type | cache.t3.micro | cache.t3.small |
| Redis cache nodes | 1 | 2 |
| Redis Multi-AZ/failover | No | Yes |

## 3. Monthly cost breakdown

The following estimates use the configured baseline capacity.

| Cost component | Development | Production |
|---|---:|---:|
| EKS control plane | $73.00 | $73.00 |
| EC2 worker nodes | $30.37 | $60.74 |
| RDS compute | $13.14 | $49.64 |
| RDS gp3 storage | $2.30 | $11.50 |
| ElastiCache Redis | $12.41 | $49.64 |
| NAT Gateway hourly charges | $32.85 | $65.70 |
| NAT Gateway public IPv4 | $3.65 | $7.30 |
| **Estimated monthly total** | **$167.72** | **$317.52** |

**Combined estimated monthly baseline: $485.24**

### Pricing calculations

- EKS: 1 cluster x $0.10/hour x 730 hours = $73.00 per environment.
- EC2: t3.medium at approximately $0.0416/hour = $30.37 per node/month.
- RDS development: db.t3.micro at approximately $0.018/hour = $13.14/month.
- RDS production: db.t3.small at approximately $0.034/hour, with Multi-AZ compute estimated at twice the Single-AZ rate = $49.64/month.
- RDS storage: gp3 estimated at $0.115/GB-month for Single-AZ. Production Multi-AZ storage is estimated at twice that rate.
- Redis development: cache.t3.micro at approximately $0.017/hour = $12.41/month.
- Redis production: 2 x cache.t3.small at approximately $0.034/hour each = $49.64/month.
- NAT Gateway: approximately $0.045/hour per gateway. Public IPv4 is estimated at $0.005/hour per NAT Gateway.

Storage autoscaling maximums are limits, not immediately billed capacity. The estimate uses the initially allocated storage.

## 4. Autoscaling impact

The baseline assumes one development worker and two production workers.

Each additional t3.medium worker adds approximately **$30.37/month** if it runs continuously.

| Environment | Baseline nodes | Maximum nodes | Additional monthly cost at maximum |
|---|---:|---:|---:|
| Development | 1 | 2 | $30.37 |
| Production | 2 | 3 | $30.37 |

If both environments remain at their configured maximum node counts for a full month, the combined estimate increases by approximately $60.74 to **$545.98/month**.

## 5. Costs not included

The following costs are excluded because they depend on implementation details or actual usage, or are not explicitly provisioned by the current Terraform configuration:

- NAT Gateway data processing, approximately $0.045 per GB processed.
- Internet data transfer and cross-Availability-Zone traffic.
- Additional public IPv4 addresses beyond the NAT Gateway addresses estimated above.
- Application Load Balancer or Network Load Balancer. No ALB/NLB resource is currently defined in the Terraform configuration.
- CloudWatch log ingestion, retention, metrics, and alarms.
- RDS backup storage beyond the applicable included allowance and additional manual snapshots.
- Additional RDS storage consumed through storage autoscaling.
- S3 storage, requests, and data transfer.
- Secrets Manager, KMS requests, and other optional managed services.
- Route 53 hosted zones and DNS queries.
- Support plans, taxes, and currency conversion fees.

The actual total will vary with application traffic, log volume, storage growth, backup consumption, and network usage.

## 6. Cost optimization recommendations

1. **Development environment scheduling:** Stop non-production RDS and Redis resources outside working hours where operational requirements permit. Evaluate whether the development EKS environment can also be stopped when unused.
2. **NAT Gateway optimization:** Use S3 and DynamoDB gateway endpoints where appropriate to avoid routing supported service traffic through NAT Gateways. Review interface endpoint costs before adding them.
3. **Capacity rightsizing:** Monitor CPU and memory utilization before changing worker, RDS, or Redis instance sizes.
4. **Commitment discounts:** Consider Compute Savings Plans or suitable Reserved Instances after workloads and capacity requirements become predictable.
5. **Autoscaling:** Keep worker node minimums appropriate to availability requirements and scale out only when workload demand requires it.
6. **Storage management:** Review RDS storage growth, backup retention, and snapshot lifecycle policies regularly.
7. **Cost visibility:** Configure AWS Budgets and cost anomaly alerts before production launch.

Production availability and recovery requirements should take priority over savings that would remove required redundancy.

## 7. Scope and limitations

- This document estimates the AWS resources described by the Terraform configuration; it does not represent deployed infrastructure or measured consumption.
- The estimate assumes both EKS clusters use Kubernetes versions under standard support. Extended support would increase the EKS control-plane charge.
- Production RDS compute and storage use approximate Multi-AZ pricing assumptions.
- NAT Gateway processing and data transfer charges are usage-dependent and are not included in the fixed baseline.
- No load balancer charge is included because no ALB/NLB resource is currently defined.
- Prices are indicative and should be checked with the AWS Pricing Calculator before deployment.

## 8. Pricing references

- [Amazon EKS pricing](https://aws.amazon.com/eks/pricing/)
- [Amazon EC2 On-Demand pricing](https://aws.amazon.com/ec2/pricing/on-demand/)
- [Amazon RDS pricing](https://aws.amazon.com/rds/pricing/)
- [Amazon ElastiCache pricing](https://aws.amazon.com/elasticache/pricing/)
- [Amazon VPC pricing](https://aws.amazon.com/vpc/pricing/)
- [NAT Gateway pricing details](https://docs.aws.amazon.com/vpc/latest/userguide/nat-gateway-pricing.html)
- [AWS Pricing Calculator](https://calculator.aws/)
