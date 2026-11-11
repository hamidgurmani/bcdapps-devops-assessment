# RideFlow DevOps Troubleshooting Log

This document records actual DevOps implementation and operational issues encountered during the BCDAPPS Senior DevOps Engineer assessment.

It covers container registry authentication, CI/CD, Kubernetes networking, application deployment, and monitoring. Each entry records the observed problem, investigation, root cause, corrective action, verification, and relevant operational lesson.

Local machine setup and application-development environment issues are intentionally excluded. No credentials or secret values are recorded.

## 1. GHCR Authentication Failure During Deployment

**Area:** Docker image registry / GitHub Actions

**Problem:** The deployment workflow could not reliably authenticate with GitHub Container Registry (GHCR) to pull the application images.

**Investigation:** Reviewed the deployment workflow's Docker login and image pull steps, along with the permissions available to the workflow token.

**Root cause:** The workflow did not have the required package read permission for GHCR authentication.

**Resolution:**
- Added the `packages: read` permission to the workflow.
- Used the GitHub-provided `GITHUB_TOKEN` to authenticate with GHCR.
- Configured Docker authentication through a temporary Docker configuration directory.
- Kept authentication and image operations within the deployment job.

**Verification:** The deployment workflow completed successfully after the authentication changes.

**Lesson:** CI/CD workflows need explicitly scoped registry permissions. Registry credentials should be handled through the platform's supported secret or token mechanism, not hardcoded in workflow files.

## 2. Docker Configuration Variable at Invalid GitHub Actions Scope

**Area:** Docker / GitHub Actions workflow configuration

**Problem:** The deployment workflow used `runner.temp` in a job-level environment variable, where that context was not valid.

**Investigation:** Reviewed the GitHub Actions workflow expression scope and the steps that perform Docker authentication, image operations, and cleanup.

**Root cause:** The runner temporary directory expression was defined at job level instead of being evaluated within individual steps.

**Resolution:**
- Removed the invalid job-level `DOCKER_CONFIG` definition.
- Defined `DOCKER_CONFIG: \${{ runner.temp }}/docker-config` separately in the Docker authentication, image pull/load, and cleanup steps.
- Kept cleanup configured to run even when an earlier step fails.

**Verification:** The corrected workflow passed. The change was committed as `86108be` (`Fix Docker config runner temp scope`).

**Lesson:** GitHub Actions contexts have scope restrictions. Validate expressions at the level where they are used, and clean up temporary authentication configuration even after failed operations.

## 3. Alembic Migration Configuration in CI

**Area:** CI pipeline / database migrations

**Problem:** The migration command needed to locate the Alembic configuration when the workflow executed from the backend directory.

**Investigation:** Checked the repository layout and tested whether Alembic could load the root-level configuration and discover the migration revision.

**Root cause:** The migration command needed an explicit path to `alembic.ini` because it was outside the backend working directory.

**Resolution:** Used the explicit configuration path:

\`\`\`bash
alembic -c ../alembic.ini upgrade head
\`\`\`

**Verification:** Ran the Alembic heads command from the backend directory:

\`\`\`bash
./.venv/bin/alembic -c ../alembic.ini heads
\`\`\`

It successfully returned the expected migration head, `0001_create_rides`.

**Lesson:** CI commands must account for the workflow's working directory. Use explicit configuration paths when project configuration is stored outside that directory.

## 4. Frontend API Requests Returning 404

**Area:** Kubernetes networking / NGINX Ingress

**Problem:** Frontend API requests returned HTTP 404 when the frontend was accessed through its Kubernetes Service port-forward.

**Investigation:** Compared the direct frontend Service access path with the intended application access path through NGINX Ingress.

**Root cause:** The frontend used relative API paths. Accessing the frontend Service directly bypassed Ingress, so API requests were sent to the frontend rather than routed to the backend.

**Resolution:**
- Used NGINX Ingress as the single entry point.
- Configured `/api` requests to route to the backend Service.
- Configured `/` requests to route to the frontend Service.
- Tested the application through the Ingress port-forward instead of directly through the frontend Service.

**Verification:** The frontend successfully fetched backend data through Ingress, and the user interface and its ride-management functionality worked as expected.

**Lesson:** Test applications through their intended network entry point. Direct Service access can bypass routing rules and produce results that do not represent the deployed application architecture.

## 5. Grafana Dashboard Performance and Resource Limits

**Area:** Kubernetes resource management / monitoring

**Problem:** Grafana was not reliably displaying the RideFlow dashboard data in the local monitoring environment.

**Investigation:** Checked the Grafana StatefulSet resource configuration and pod health.

**Root cause:** The configured Grafana resource limits were insufficient for the workload in the local Kubernetes environment.

**Resolution:** Increased the Grafana container resources:

\`\`\`bash
kubectl set resources statefulset/monitoring-grafana -n monitoring \
  -c grafana \
  --requests=cpu=100m,memory=256Mi \
  --limits=cpu=750m,memory=1Gi
\`\`\`

**Verification:** The Grafana rollout completed successfully. The pod became ready with all three containers running and zero restarts. The RideFlow dashboard subsequently displayed monitoring data.

**Lesson:** Monitoring components also need appropriate resource requests and limits. Resource constraints can affect observability itself, even when the monitored application is healthy.

## 6. Unexpected Alertmanager Crash-Loop Alert

**Area:** Prometheus / Alertmanager monitoring

**Problem:** Alertmanager displayed a firing `AlertmanagerClusterCrashlooping` alert even though the current Alertmanager pod was running and ready.

**Investigation:**
- Checked monitoring pod readiness and restart counts.
- Checked the Alertmanager container's process start time.
- Reviewed recent Alertmanager logs.
- Queried Prometheus process start-time metrics.

**Observations:** The current Alertmanager pod was ready with zero reported container restarts, and the recent log query returned no relevant entries. However, Prometheus reported unexpected changes in the process start-time metric used by the alert expression.

**Status:** Unresolved. The available checks did not establish the underlying cause. The alert should not be treated as proof of a current Alertmanager container crash.

**Next investigation:** Review the alert expression and the source and stability of the process start-time metric. Confirm whether the alert is caused by metric behavior, stale time series, or an actual process restart pattern before changing the alert rule.

**Lesson:** Validate an alert against the underlying metrics and current workload state. A firing alert is a signal to investigate, not sufficient evidence by itself to establish root cause.

---

## Scope and Verification Notes

- The local Docker Compose application was verified with healthy services and working application functionality.
- Kubernetes workloads and application routing were tested on a local kind cluster.
- Terraform configurations were formatted and validated, but AWS infrastructure was not provisioned.
- CI and the development deployment workflows completed successfully after the recorded corrections.
- Prometheus metrics, the RideFlow Grafana dashboard, and the three RideFlow alert rules were verified as loaded.
- Actual firing and notification delivery of the RideFlow-specific alert rules have not been demonstrated.
- The Alertmanager crash-loop alert remains an unresolved investigation item.
