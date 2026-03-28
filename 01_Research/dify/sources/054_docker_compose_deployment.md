---
source_id: "054"
title: "Deploy Dify with Docker Compose - Dify Docs"
url: "https://docs.dify.ai/en/self-host/quick-start/docker-compose"
type: "documentation"
scraped_at: "2026-03-27"
keywords: ["Dify Docker deployment", "Dify Docker Compose", "Dify self-hosting"]
content_length: 4680
---

# Deploy Dify with Docker Compose

## Before Deployment

Minimum system requirements:

### Hardware
- CPU >= 2 Core
- RAM >= 4 GiB

### Software

| Operating System | Required Software | Notes |
|---|---|---|
| macOS 10.14+ | Docker Desktop | Configure with at least 2 virtual CPUs and 8 GiB of memory |
| Linux | Docker 19.03+, Docker Compose 1.28+ | |
| Windows with WSL 2 | Docker Desktop | Store source code and data in Linux file system rather than Windows |

## Deploy and Start Dify

### Step 1: Clone Dify

Clone the Dify source code to your local machine:

```bash
git clone --branch "$(curl -s https://api.github.com/repos/langgenius/dify/releases/latest | jq -r .tag_name)" https://github.com/langgenius/dify.git
```

### Step 2: Start Dify

1. Navigate to the docker directory:

```bash
cd dify/docker
```

2. Copy the example environment configuration file:

```bash
cp .env.example .env
```

Note: When the frontend and backend run on different subdomains, set COOKIE_DOMAIN to the site's top-level domain (e.g., example.com) and set NEXT_PUBLIC_COOKIE_DOMAIN to 1 in the .env file.

3. Start the containers:

```bash
# Docker Compose V2
docker compose up -d

# Docker Compose V1
docker-compose up -d
```

The following containers will be started:
- 5 core services: api, worker, worker_beat, web, plugin_daemon
- 6 dependent components: weaviate, db_postgres, redis, nginx, ssrf_proxy, sandbox

4. Verify all containers are running:

```bash
docker compose ps
```

Expected containers and their images:
- docker-api-1: langgenius/dify-api
- docker-db_postgres-1: postgres:15-alpine
- docker-nginx-1: nginx:latest (ports 80, 443)
- docker-plugin_daemon-1: langgenius/dify-plugin-daemon (port 5003)
- docker-redis-1: redis:6-alpine
- docker-sandbox-1: langgenius/dify-sandbox
- docker-ssrf_proxy-1: ubuntu/squid:latest
- docker-weaviate-1: semitechnologies/weaviate:1.27.0
- docker-web-1: langgenius/dify-web
- docker-worker-1: langgenius/dify-api
- docker-worker_beat-1: langgenius/dify-api

## Access Dify

1. Open the administrator initialization page:

```
# Local environment
http://localhost/install

# Server environment
http://your_server_ip/install
```

2. After completing admin account setup, log in at:

```
http://localhost
# or
http://your_server_ip
```

## Customize Dify

Modify the environment variable values in your local .env file, then restart:

```bash
docker compose down
docker compose up -d
```

## Upgrade Dify

Upgrade steps may vary between releases. Refer to the upgrade guide on the Releases page. After upgrading, check whether the .env.example file has changed and update your local .env file accordingly.
