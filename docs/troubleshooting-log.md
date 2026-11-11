# RideFlow Troubleshooting Log

This document records significant development, testing and containerization issues encountered during the BCDAPPS Senior DevOps Engineer assessment.

It focuses on diagnosis, root causes, corrective actions and lessons learned. Local credentials and secret values are intentionally excluded.

## 1. Python Virtual Environment

**Problem:** Creating the backend virtual environment initially failed because the required Python venv package was missing.

**Diagnosis:** The system Python installation did not have the required virtual environment support package.

**Resolution:** Installed the matching Python venv package through the Ubuntu package manager and recreated the virtual environment.

**Lesson:** Verify runtime and development prerequisites before installing application dependencies.

## 2. Database Test Authentication

**Problem:** Backend tests initially could not authenticate against PostgreSQL.

**Diagnosis:** The test command was using a placeholder database password rather than the actual local environment configuration.

**Resolution:** Read the password locally from the ignored environment file through a shell variable. Ran tests against the dedicated `rideflow_test` database and Redis database index `1`.

**Safety:** Credentials were not added to source code or documentation.

**Lesson:** Separate test resources from development data and keep credentials outside the repository.
