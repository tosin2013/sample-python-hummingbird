# sample-python-hummingbird

A sample Python ML application (Flask + scikit-learn) built on Red Hat Hummingbird container images for the Zero-CVE Hummingbird Workshop.

## Quick Start

```bash
# Build
podman build -f Containerfile -t sample-python-hummingbird:latest .

# Run
podman run -d --name python-ml-demo -p 8080:8080 sample-python-hummingbird:latest

# Test
curl http://localhost:8080/
curl http://localhost:8080/health
curl http://localhost:8080/predict/sample
curl -X POST http://localhost:8080/predict \
  -H "Content-Type: application/json" \
  -d '{"features": [5.1, 3.5, 1.4, 0.2]}'
```

## Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Runtime info (Python version, scikit-learn version, numpy version) |
| `/health` | GET | Health check |
| `/predict` | POST | Iris classification from features array |
| `/predict/sample` | GET | Sample prediction for quick testing |

## Container Images

- **Builder**: `registry.access.redhat.com/ubi9/python-311:latest`
- **Runtime**: `quay.io/hummingbird-hatchling/python:3.11`

## Security & CI/CD

This repository implements a **Zero-CVE security pipeline** using GitHub Actions with automated SBOM generation and vulnerability scanning.

### Zero-CVE CI/CD Pipeline

```mermaid
flowchart TD
    A[Git Push to main] --> B[GitHub Actions Trigger]
    B --> C[Python Build & Test]
    B --> D[Container Build]
    B --> E[Security Scan]

    C --> C1[Install Dependencies]
    C1 --> C2[Verify Flask App]
    C2 --> C3[Verify ML Model]

    D --> D1[Build with Buildah]
    D1 --> D2[Inspect Image]
    D2 --> D3[Verify Non-Root User]
    D3 --> D4[Upload Image Config]

    E --> E1[Build Container Image]
    E1 --> E2[Generate SBOM with Syft]
    E2 --> E3[Scan with Grype]
    E3 --> E4{CVEs Found?}

    E4 -->|Critical/High| E5[FAIL - Block Merge]
    E4 -->|None/Low/Medium| E6[PASS - Upload Artifacts]

    E6 --> E7[Upload SBOM]
    E6 --> E8[Upload Grype Report]

    style E5 fill:#ff6b6b
    style E6 fill:#51cf66
    style E7 fill:#748ffc
    style E8 fill:#748ffc
```

### Vulnerability Gating Policy

```mermaid
flowchart LR
    A[Grype Scan] --> B{Severity Check}

    B -->|Critical: > 0| C[❌ FAIL BUILD]
    B -->|High: > 0| C
    B -->|Medium: Any| D[⚠️ WARN - Continue]
    B -->|Low: Any| D
    B -->|None| E[✅ PASS]

    C --> F[Exit Code 1<br/>Block PR Merge]
    D --> G[Upload Report<br/>Allow Merge]
    E --> G

    style C fill:#ff6b6b,color:#fff
    style D fill:#ffd43b
    style E fill:#51cf66,color:#fff
```

**Zero-Tolerance Policy:**
- **Critical**: 0 allowed → Build fails
- **High**: 0 allowed → Build fails
- **Medium/Low**: Tracked but don't block deployment

### Hummingbird Multi-Stage Build

```mermaid
flowchart TB
    subgraph Stage1[Stage 1: Builder - UBI9 Python 3.11]
        A1[FROM ubi9/python-311:latest]
        A2[Install dependencies<br/>pip install -r requirements.txt]
        A3[Copy application code]
        A1 --> A2 --> A3
    end

    subgraph Stage2[Stage 2: Runtime - Hummingbird Python 3.11]
        B1[FROM hummingbird/python:3.11]
        B2[Copy app + dependencies<br/>from builder stage]
        B3[Set non-root user UID 65532]
        B4[Expose port 8080]
        B5[CMD python main.py]
        B1 --> B2 --> B3 --> B4 --> B5
    end

    Stage1 -->|Copy artifacts| Stage2

    subgraph Result[Final Image Characteristics]
        R1[Size: ~95-120 MB vs 400+ MB UBI]
        R2[CVEs: 0 at ship time]
        R3[Packages: Minimal runtime only]
        R4[User: Non-root UID 65532]
    end

    Stage2 --> Result

    style Stage1 fill:#339af0
    style Stage2 fill:#51cf66
    style Result fill:#748ffc
```

### Complete Security Workflow

```mermaid
flowchart TD
    A[Developer commits code] --> B[CI: Build multi-stage image]
    B --> C[CI: Generate SBOM with Syft]
    C --> D[CI: Scan with Grype]

    D --> E{CVE Threshold<br/>Exceeded?}
    E -->|Yes| F[Build Fails<br/>Developer fixes]
    E -->|No| G[Upload SBOM Artifact]

    F --> A
    G --> H[Upload Grype Report]
    H --> I[Image ready for deployment]

    I --> J[Runtime: Non-root user]
    I --> K[Runtime: Minimal attack surface]
    I --> L[Runtime: Zero-CVE baseline]

    style F fill:#ff6b6b,color:#fff
    style I fill:#51cf66,color:#fff
    style J fill:#748ffc
    style K fill:#748ffc
    style L fill:#748ffc
```

### Security Tools

| Tool | Purpose | Stage |
|------|---------|-------|
| **Syft** | SBOM generation (SPDX JSON + JSON) | CI Pipeline |
| **Grype** | Vulnerability scanning with severity thresholds | CI Pipeline |
| **Buildah** | Rootless container builds | CI Pipeline |
| **GitHub Actions** | Artifact storage (SBOMs + scan reports) | CI Platform |

### Hummingbird Advantages

**Image Size Reduction:**
- Traditional UBI Python: ~400+ MB
- Hummingbird Python: ~95-120 MB
- **Reduction: 70-80%**

**Security Posture:**
- Traditional UBI: 15-30+ CVEs (even in recent versions)
- Hummingbird: **0 CVEs at ship time**
- Attack surface: Minimal runtime packages only

**Compliance:**
- Automated SBOM generation (SPDX JSON format)
- Retained for 30 days in GitHub Actions artifacts
- Ready for NIST and EU Cyber Resilience Act requirements

## Workshop Usage

This repo is used in **Module 2.2: Custom Build Strategies** of the Zero-CVE Hummingbird Workshop to demonstrate the `hummingbird-multi-lang` Shipwright strategy auto-detecting Python from `requirements.txt`.
