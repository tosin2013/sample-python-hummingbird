ARG BUILDER_IMAGE=registry.access.redhat.com/ubi9/python-311:latest
ARG RUNTIME_IMAGE=quay.io/hummingbird-hatchling/python:3.11

# Stage 1: Build wheels with full UBI Python (pip, compilers, headers)
FROM ${BUILDER_IMAGE} AS builder

WORKDIR /opt/app-root/src

COPY --chown=1001:1001 requirements.txt ./
RUN pip wheel --no-cache-dir --wheel-dir /opt/app-root/wheels -r requirements.txt

# Stage 2: Runtime on Hummingbird Python
FROM ${RUNTIME_IMAGE}

WORKDIR /app

COPY --from=builder /opt/app-root/wheels /opt/app-root/wheels
RUN python3 -m pip install --user --no-cache-dir --no-index \
    --find-links=/opt/app-root/wheels /opt/app-root/wheels/*

COPY --chown=1001:1001 src/ ./src/
COPY --chown=1001:1001 gunicorn.conf.py ./

USER 65532

ENV PATH="/tmp/.local/bin:${PATH}"

EXPOSE 8080

CMD ["python3", "-m", "gunicorn", \
     "--config", "gunicorn.conf.py", \
     "src.main:app"]
