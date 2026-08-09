# PragatiX Backend Pipeline Guide

Quick overview of the backend CI/CD and security setups for the Spring Boot service.

## Workflows

- `01-backend-ci.yml`: Runs unit tests, compiles Java 21 code, checks JaCoCo code coverage, runs Checkstyle/PMD/SpotBugs, and packages the runnable JAR artifact.
- `02-backend-security.yml`: Runs security tools (Gitleaks, Semgrep, CodeQL, Trivy, OWASP Dependency-Check, SBOM) and builds the HTML dashboard.
- `03-backend-deploy.yml`: Packages the Spring Boot JAR and runs build/test checks with a MySQL integration container.

## Local Scan

To run the security scan locally on Windows:

```powershell
cd N:\pragatiX
.\scripts\generate-security-report.ps1
```

This merges the reports and opens `final-security-report.html` in your default browser.

## Pipeline Switches

Set at the top of each workflow file under `env:`:

- `GATE_MODE`: Set to `report-only` so findings are tracked on the dashboard without blocking PRs during tuning. Change to `block` to enforce.
- `COVERAGE_THRESHOLD`: Minimum line coverage percentage (currently `40%`).
- `SONAR_ENABLED`: Defaults to `false` because SonarQube runs locally (`127.0.0.1:9000`), which GitHub runners can't reach.

## Required Secrets & Variables

Add these under **Settings -> Secrets and variables -> Actions**:

- `TEST_DB_PASSWORD` (Secret): Optional password for test DB container.
- `SONAR_TOKEN` (Secret): Only needed if `SONAR_ENABLED` is set to `true`.
- `SONAR_HOST_URL` (Secret): Only needed if `SONAR_ENABLED` is set to `true`.
- `GITLEAKS_LICENSE` (Secret): Optional Gitleaks Pro license key.

## Security Gate

The security gate (`security-gate.sh`) evaluates JaCoCo coverage, unit test results, Gitleaks secrets, and critical vulnerabilities. In `report-only` mode, it logs failures and generates a GitHub step summary without failing the workflow run.
