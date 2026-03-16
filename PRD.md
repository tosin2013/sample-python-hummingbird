# Product Requirements Document: sample-python-hummingbird

## Purpose

A sample Python ML application built on Red Hat Hummingbird container images,
used as the Python test case for Module 2.2 (Custom Build Strategies) in the
Zero-CVE Hummingbird Workshop.

Demonstrates that Hummingbird images can run real ML workloads (scikit-learn,
numpy) while maintaining a zero-CVE posture at the OS layer.

## Repository

- **Owner**: tosin2013 (Tosin Akinosho, takinosh@redhat.com)
- **Name**: `sample-python-hummingbird`
- **Visibility**: Public

## Application Requirements

| Requirement             | Detail                                              |
|------------------------|-----------------------------------------------------|
| Language               | Python 3.11                                          |
| Framework              | Flask + gunicorn                                     |
| ML Libraries           | scikit-learn, numpy                                  |
| Port                   | 8080                                                 |
| Endpoints              | `GET /` (info), `GET /health`, `POST /predict`, `GET /predict/sample` |
| Container user         | 65532 (non-root)                                     |
| Builder image          | `registry.access.redhat.com/ubi9/python-311:latest`  |
| Runtime image          | `quay.io/hummingbird-hatchling/python:3.11`          |
| Build pattern          | Multi-stage Containerfile (pip install in builder, copy to runtime) |

## Endpoints

- `GET /` -- Returns JSON with runtime info, ML backend version, numpy version
- `GET /health` -- Returns `{"status": "healthy"}`
- `POST /predict` -- Iris classification: accepts `{"features": [5.1, 3.5, 1.4, 0.2]}`
- `GET /predict/sample` -- Runs prediction on a hardcoded sample for quick testing

## CI/CD

- **GitHub Actions**: Build, container build validation, grype security scan (fails on High/Critical), SBOM generation
- **Dependabot**: Weekly pip and GitHub Actions updates

## Verification

```bash
# Local test
curl http://localhost:8080/
curl http://localhost:8080/health
curl http://localhost:8080/predict/sample
curl -X POST http://localhost:8080/predict -H "Content-Type: application/json" \
  -d '{"features": [5.1, 3.5, 1.4, 0.2]}'
```
