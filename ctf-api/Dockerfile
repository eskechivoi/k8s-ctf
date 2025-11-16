# --- STAGE 1: BUILD (Install Python and Helm dependencies) ---
FROM python:3.12.12-slim-trixie as build

RUN apt-get update && apt-get install -y \
    curl \
    tar \
    gzip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 1. Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2. Install Helm
ENV HELM_VERSION=v3.14.0
RUN curl -sSL https://get.helm.sh/helm-${HELM_VERSION}-linux-amd64.tar.gz | tar xz \
    && mv linux-amd64/helm /usr/local/bin/helm \
    && chmod +x /usr/local/bin/helm \
    && rm -rf linux-amd64

# --- STAGE 2: RUNTIME ---
FROM python:3.12.12-slim-trixie

RUN apt-get update && apt-get install -y \
    tar \
    gzip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /src

COPY --from=build /usr/local/lib/python3.12/site-packages/ /usr/local/lib/python3.12/site-packages/
COPY --from=build /usr/local/bin/gunicorn /usr/local/bin/

COPY --from=build /usr/local/bin/helm /usr/local/bin/helm

COPY gunicorn_config.py .
COPY main.py .
COPY app ./app

ENV PARENT_CHART_PATH="/mnt/challenge-commons"
ENV FLASK_APP="main.py"
ENV CHALLENGES_NAMESPACE="ctf-challenges"

EXPOSE 8000

CMD ["gunicorn", "--config", "/src/gunicorn_config.py", "main:app"]