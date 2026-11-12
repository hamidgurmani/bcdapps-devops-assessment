# RideFlow Incident Response Runbooks

## Purpose and Scope

This document provides operational procedures for four hypothetical failure scenarios identified in the BCDAPPS Senior DevOps Engineer assessment. These are runbooks, not claims that these incidents occurred during implementation.

## General Incident Handling

1. Confirm the affected environment and scope.
2. Assess customer impact and severity.
3. Preserve logs, events, and diagnostic information.
4. Identify the failure domain before changing resources.
5. Apply the safest mitigation.
6. Verify service recovery using health checks and functional tests.
7. Record root cause, actions, and preventive measures.

Use the correct Kubernetes context and namespace. The examples use `rideflow-dev`.

---

## 1. Kubernetes CrashLoopBackOff

### Symptoms and Impact

- A pod repeatedly terminates and restarts.
- Desired replicas are not ready.
- Application requests may fail or become unavailable.

### Investigation

```bash
kubectl get pods -n rideflow-dev
kubectl describe pod <pod-name> -n rideflow-dev
kubectl logs <pod-name> -n rideflow-dev
kubectl logs <pod-name> -n rideflow-dev --previous
kubectl get events -n rideflow-dev --sort-by=.lastTimestamp
kubectl get deployments -n rideflow-dev
kubectl rollout history deployment/<deployment-name> -n rideflow-dev
```

### Possible Root Causes

- Invalid application configuration or missing environment variables.
- Incorrect Secret or ConfigMap references.
- Database or Redis connectivity failures.
- Container startup command or image errors.
- Failed startup or liveness probes.
- Memory limits causing OOMKilled termination.
- Insufficient permissions or filesystem access.

### Mitigation and Recovery

1. Use pod events and previous-container logs to identify the failure.
2. Check configuration references without exposing secret values.
3. Verify PostgreSQL and Redis availability and connectivity.
4. Correct the faulty image, configuration, or resource settings.
5. Apply the corrected manifest or deploy a known-good image.
6. If a recent rollout introduced the failure, consider rolling back:

```bash
kubectl rollout undo deployment/<deployment-name> -n rideflow-dev
```

7. Verify recovery:

```bash
kubectl rollout status deployment/<deployment-name> -n rideflow-dev
kubectl get pods -n rideflow-dev
```

Confirm application health and perform a functional API test before closing the incident.

### Prevention

- Configure appropriate readiness, liveness, and startup probes.
- Validate configuration before deployment.
- Use immutable image tags tied to commit SHAs.
- Configure realistic CPU and memory requests and limits.
- Monitor restart counts, pod availability, and application health.
- Test deployment changes in development before production.

---

## 2. High CPU Utilization or Increased Traffic

### Symptoms and Impact

- API response times increase.
- CPU utilization approaches configured limits.
- Requests time out or return HTTP 5xx errors.
- Pods may be throttled or restarted due to resource pressure.
- HPA may scale replicas or fail to scale if metrics are unavailable.

### Investigation

Check node and pod resource usage:

```bash
kubectl top nodes
kubectl top pods -n rideflow-dev
```

Inspect deployment resources and replica counts:

```bash
kubectl get deployments -n rideflow-dev
kubectl describe deployment rideflow-backend -n rideflow-dev
```

Inspect HPA status and scaling events:

```bash
kubectl get hpa -n rideflow-dev
kubectl describe hpa -n rideflow-dev
```

Review recent events:

```bash
kubectl get events -n rideflow-dev --sort-by=.lastTimestamp
```

Review Prometheus metrics and Grafana panels for request rate, HTTP 5xx rate, API latency, and backend availability.
### Possible Root Causes
- Sudden legitimate traffic increase.
- Inefficient application code or expensive API requests.
- Database query bottlenecks or connection exhaustion.
- Redis cache misses or cache unavailability.
- CPU requests or limits that are too low.
- HPA metrics unavailable or incorrect scaling thresholds.
- Traffic abuse or an unexpected request pattern.
### Mitigation and Recovery
1. Determine whether the traffic increase is legitimate or abnormal.
2. Identify the affected application component using pod metrics and dashboards.
3. If capacity is insufficient, scale the backend within safe resource limits:

```bash
kubectl scale deployment/rideflow-backend --replicas=3 -n rideflow-dev
```

4. Check whether HPA is managing the deployment. Avoid competing manual scaling changes with HPA.
5. If database pressure is responsible, inspect connections and slow queries before increasing application replicas.
6. Apply rate limiting or upstream traffic controls if abnormal traffic is confirmed and suitable controls are available.
7. Verify recovery through request latency, error rate, pod readiness, and application health.
### Prevention
- Configure and validate HPA CPU utilization targets and replica limits.
- Set appropriate resource requests and limits.
- Monitor traffic, latency, saturation, and error rates.
- Optimize expensive queries and frequently used API paths.
- Use caching where appropriate.
- Perform load testing and capacity planning before production releases.
  
---

## 3. PostgreSQL Outage or Database Connectivity Failure

### Symptoms and Impact

- Backend health checks or database-dependent API requests fail.
- Ride creation and retrieval operations return errors.
- Backend logs show connection timeouts, refused connections, or authentication errors.
- PostgreSQL pods are unavailable or not ready.
- Application requests may return HTTP 5xx responses.

### Investigation

Check PostgreSQL pods and StatefulSet:

```bash
kubectl get pods -n rideflow-dev
kubectl get statefulsets -n rideflow-dev
kubectl describe statefulset rideflow-postgres -n rideflow-dev
```

Inspect PostgreSQL logs:

```bash
kubectl logs statefulset/rideflow-postgres -n rideflow-dev
```

Inspect persistent volume claims:

```bash
kubectl get pvc -n rideflow-dev
kubectl describe pvc -n rideflow-dev
```

Check the PostgreSQL service and endpoints:

```bash
kubectl get svc,endpoints -n rideflow-dev
```

Inspect backend logs for database connection errors:

```bash
kubectl logs deployment/rideflow-backend -n rideflow-dev --tail=100
```

### Possible Root Causes
- PostgreSQL pod crash or failed readiness probe.
- Persistent volume unavailable or out of storage.
- Incorrect database hostname, port, or credentials.
- Network connectivity or service endpoint problems.
- Database connection exhaustion.
- Database recovery after an unclean shutdown.
- Corrupt data or failed database migration.
### Mitigation and Recovery
1. Determine whether the failure is isolated to the application connection or the PostgreSQL service itself.
2. Check PostgreSQL pod events and logs before restarting or modifying workloads.
3. Verify the service selector, endpoints, persistent volume status, and available storage.
4. Correct database configuration or connectivity issues if identified.
5. If the PostgreSQL pod has failed, follow its logs and events to determine whether a controlled restart or configuration correction is appropriate.
6. Do not delete the StatefulSet, PVC, or database volume as a troubleshooting shortcut.
7. If data corruption or unrecoverable storage failure is confirmed, follow the approved backup restoration procedure. Preserve the original volume where possible.
8. Verify PostgreSQL readiness and backend database connectivity.
9. Test ride creation and retrieval before declaring recovery.
### Prevention
- Use persistent volumes for database storage.
- Monitor database availability, storage capacity, connections, and query performance.
- Configure appropriate readiness and liveness probes.
- Protect database credentials and validate secret references.
- Schedule regular backups and periodically test restoration.
- Document recovery objectives, including RPO and RTO, for production.
- Test database failure and recovery procedures before production use.
  
---

## 4. Production Secret or Credential Compromise

### Symptoms and Impact

- A credential, token, private key, or database password is exposed in a repository, log, build artifact, or public location.
- Unauthorized access or suspicious API activity is detected.
- An exposed credential may allow access to cloud resources, databases, Kubernetes, or CI/CD systems.

### Immediate Containment

1. Treat the credential as compromised. Do not wait for proof of misuse.
2. Identify the affected credential, associated systems, and permissions.
3. Restrict or revoke the exposed credential immediately.
4. Disable affected access keys or tokens where possible.
5. If a production workload depends on the credential, coordinate rotation to avoid unnecessary service disruption.
6. Preserve relevant audit logs and evidence. Do not publish the exposed value in incident tickets or investigation notes.

### Investigation

Review the exposure source:

- Git history and repository visibility.
- GitHub Actions logs and workflow configuration.
- Container image layers and build artifacts.
- Application logs and Kubernetes configuration.
- Access logs and cloud audit events.

For Kubernetes, identify the affected Secret without printing its values:

```bash
kubectl get secrets -n rideflow-prod
kubectl describe secret <secret-name> -n rideflow-prod
```

Review relevant workloads and configuration references:

```bash
kubectl describe deployment <deployment-name> -n rideflow-prod
kubectl get events -n rideflow-prod --sort-by=.lastTimestamp
```

For AWS environments, review CloudTrail events and the IAM activity associated with the exposed identity.
### Credential Rotation and Recovery
1. Generate a new credential using the approved secret-management process.
2. Update the credential in the appropriate secret store.
3. Update affected Kubernetes Secret resources or external secret references without printing secret values.
4. Restart or roll out workloads that require the updated credential.
5. Revoke the old credential and verify it can no longer authenticate.
6. Review access logs for unauthorized activity during the exposure window.
7. Check for unauthorized resource changes, data access, or persistence mechanisms.
8. Verify application connectivity and normal service functionality using the new credential.
9. If repository history contains the secret, remove it from the repository history where appropriate. Coordinate the cleanup with repository administrators. History cleanup does not replace credential rotation.
### Prevention
- Store production secrets in AWS Secrets Manager or an equivalent managed secret provider.
- Apply least-privilege IAM permissions and rotate credentials periodically.
- Never commit credentials, private keys, or environment files.
- Use GitHub Actions secrets or short-lived workload credentials instead of hardcoded tokens.
- Enable secret scanning and review alerts promptly.
- Restrict access to production secrets and audit access.
- Avoid exposing secret values in CI logs, shell output, or application logs.
- Review credential exposure and revocation procedures periodically.

## Assessment Scope Note
These four scenarios are documented as operational response procedures. They were not deliberately triggered or claimed as completed failure simulations during the local RideFlow implementation. The PostgreSQL backup and restore procedure was separately tested locally, but production disaster recovery was not demonstrated.
