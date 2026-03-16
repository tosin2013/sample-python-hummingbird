ARG BUILDER_IMAGE=registry.access.redhat.com/ubi9/python-311:latest
ARG RUNTIME_IMAGE=quay.io/hummingbird-hatchling/python:3.11

# Stage 1: Build with full UBI Python (pip, compilers, headers)
FROM ${BUILDER_IMAGE} AS builder

WORKDIR /opt/app-root/src

COPY --chown=1001:1001 requirements.txt ./
RUN pip install --no-cache-dir \
    --prefix=/opt/app-root/install \
    -r requirements.txt

# Stage 2: Runtime on Hummingbird Python
FROM ${RUNTIME_IMAGE}

WORKDIR /app

COPY --from=builder --chown=1001:1001 /opt/app-root/install /usr/local

COPY --chown=1001:1001 src/ ./src/
COPY --chown=1001:1001 gunicorn.conf.py ./

USER 65532

EXPOSE 8080

CMD ["python3", "-m", "gunicorn", \
     "--config", "gunicorn.conf.py", \
     "src.main:app"]
