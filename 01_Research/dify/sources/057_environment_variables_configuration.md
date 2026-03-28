---
source_id: "057"
title: "Environments - Dify Docs"
url: "https://docs.dify.ai/en/self-host/configuration/environments"
type: "documentation"
scraped_at: "2026-03-27"
keywords: ["Dify environment configuration", "Dify .env variables", "Dify PostgreSQL Redis Weaviate configuration"]
content_length: 14200
---

# Environments - Dify Docs

Comprehensive environment variable reference for Dify self-hosted deployment.

## Common Variables

- **CONSOLE_API_URL**: Backend URL for the console API. Used to construct the authorization callback. Example: `https://api.console.dify.ai`
- **CONSOLE_WEB_URL**: Front-end URL of the console web interface. Used for CORS configuration. Example: `https://console.dify.ai`
- **SERVICE_API_URL**: The Service API URL, used to display Service API Base URL. Example: `https://api.dify.ai`
- **TRIGGER_URL**: Base URL prefix for webhook callback URLs in both webhook triggers and plugin triggers.
- **APP_API_URL**: WebApp API backend URL. Example: `https://app.dify.ai`
- **APP_WEB_URL**: WebApp URL for file preview/download. Example: `https://udify.app/`
- **FILES_URL**: Prefix for file preview/download URLs. Image preview URLs are signed and expire after 5 minutes.

## Server Configuration

- **MODE**: Startup mode (docker only): `api` (API Server) or `worker` (async queue worker)
- **DEBUG**: Debug mode, disabled by default
- **FLASK_DEBUG**: Flask debug mode for trace information in API responses
- **SECRET_KEY**: Secret key for signing session cookies and encrypting sensitive DB info. Generate with `openssl rand -base64 42`. Must be set before first launch.
- **DEPLOY_ENV**: `PRODUCTION` (default) or `TESTING` (distinct color label on front-end)
- **LOG_LEVEL**: Default INFO. Recommended ERROR for production.
- **MIGRATION_ENABLED**: When true, database migrations run automatically on container startup (docker only)
- **TEXT_GENERATION_TIMEOUT_MS**: Default 60000ms. Timeout for text generation and workflow processes.
- **OPENAI_API_BASE**: OpenAI base address, default `https://api.openai.com/v1`

### Container Startup Configuration (docker/docker-compose only)

- **DIFY_BIND_ADDRESS**: API service binding address, default 0.0.0.0
- **DIFY_PORT**: API service binding port, default 5001
- **SERVER_WORKER_AMOUNT**: Number of API server workers (gevent). Formula: `cpu cores x 2 + 1`
- **SERVER_WORKER_CLASS**: Default gevent. Use sync or solo on Windows.
- **GUNICORN_TIMEOUT**: Request handling timeout. Default 200, recommended 360 for long SSE connections.
- **CELERY_WORKER_CLASS**: Default gevent. Use sync or solo on Windows.
- **CELERY_WORKER_AMOUNT**: Number of Celery workers. Default 1.
- **COMPOSE_PROFILES**: Selectively start service groups. Default derived from VECTOR_STORE and DB_TYPE.

## Database Configuration (PostgreSQL)

Uses PostgreSQL with the public schema.

- **DB_TYPE**: `postgresql` (default), `mysql`, `oceanbase`, `seekdb`
- **DB_USERNAME**: Username
- **DB_PASSWORD**: Password
- **DB_HOST**: Database host
- **DB_PORT**: Database port, default 5432
- **DB_DATABASE**: Database name
- **SQLALCHEMY_POOL_SIZE**: Connection pool size, default 30
- **SQLALCHEMY_POOL_RECYCLE**: Pool recycling time, default 3600 seconds
- **SQLALCHEMY_ECHO**: Print SQL, default false

## Redis Configuration

Used for caching and pub/sub during conversation.

- **REDIS_HOST**: Redis host
- **REDIS_PORT**: Redis port, default 6379
- **REDIS_DB**: Redis Database, default 0. Use different DB from Session Redis and Celery Broker.
- **REDIS_USERNAME**: Default empty
- **REDIS_PASSWORD**: Default empty. Strongly recommended to set a password.
- **REDIS_USE_SSL**: Use SSL, default false
- **REDIS_USE_SENTINEL**: Use Redis Sentinel
- **REDIS_SENTINELS**: Sentinel nodes format: `<sentinel1_ip>:<sentinel1_port>,<sentinel2_ip>:<sentinel2_port>`
- **REDIS_SENTINEL_SERVICE_NAME**: Same as Master Name
- **REDIS_SENTINEL_USERNAME/PASSWORD**: Sentinel credentials
- **REDIS_SENTINEL_SOCKET_TIMEOUT**: Default 0.1 seconds

## Celery Configuration

- **CELERY_BROKER_URL**: Direct mode: `redis://<user>:<pass>@<host>:<port>/<db>`. Sentinel mode: `sentinel://<user>:<pass>@<host>:<port>/<db>`
- **BROKER_USE_SSL**: Use SSL, default false
- **CELERY_USE_SENTINEL**: Enable Sentinel mode, default false

## CORS Configuration

- **CONSOLE_CORS_ALLOW_ORIGINS**: Console CORS policy, default `*`
- **WEB_API_CORS_ALLOW_ORIGINS**: WebAPP CORS policy, default `*`
- **COOKIE_DOMAIN**: Set to top-level domain when frontend/backend on different subdomains
- **NEXT_PUBLIC_COOKIE_DOMAIN**: Set to `1` when frontend/backend on different subdomains

## File Storage Configuration

- **STORAGE_TYPE**: `local` (default), `s3`, `azure-blob`, `aliyun-oss`, `huawei-obs`, `volcengine-tos`, `tencent-cos`
- **STORAGE_LOCAL_PATH**: Default `storage`. Mount `/app/api/storage` in both api and worker containers.
- S3, Azure Blob, Aliyun OSS, Huawei OBS, Volcengine TOS, Tencent COS each have their own set of credentials and endpoint variables.

## Vector Database Configuration

- **VECTOR_STORE**: Supported values include: `weaviate`, `qdrant`, `milvus`, `myscale`, `relyt`, `pgvector`, `pgvecto-rs`, `chroma`, `opensearch`, `oracle`, `tencent`, `elasticsearch`, `elasticsearch-ja`, `analyticdb`, `couchbase`, `vikingdb`, `opengauss`, `tablestore`, `vastbase`, `tidb`, `baidu`, `lindorm`, `huawei_cloud`, `upstash`, `matrixone`, `clickzetta`, `alibabacloud_mysql`, `iris`, `oceanbase`, `seekdb`

### Weaviate Configuration
- **WEAVIATE_ENDPOINT**: e.g., `http://weaviate:8080`
- **WEAVIATE_API_KEY**: API key credential
- **WEAVIATE_BATCH_SIZE**: Batch creation size, default 100
- **WEAVIATE_GRPC_ENABLED**: gRPC method (better performance), default true

### Qdrant Configuration
- **QDRANT_URL**: e.g., `https://your-qdrant-cluster-url.qdrant.tech/`
- **QDRANT_API_KEY**: API key credential

### Milvus Configuration
- **MILVUS_URI**: e.g., `http://host.docker.internal:19530`
- **MILVUS_TOKEN**, **MILVUS_USER**, **MILVUS_PASSWORD**: Credentials

## Knowledge Configuration

- **UPLOAD_FILE_SIZE_LIMIT**: Max file size in MB, default 15
- **UPLOAD_FILE_BATCH_LIMIT**: Max batch files, default 5
- **ETL_TYPE**: `dify` (proprietary) or `Unstructured` (Unstructured.io)
- **TOP_K_MAX_VALUE**: Max top-k for RAG, default 10

## Multi-modal Configuration

- **MULTIMODAL_SEND_IMAGE_FORMAT**: `base64` (default) or `url`
- **UPLOAD_IMAGE_FILE_SIZE_LIMIT**: Default 10M

## Scheduled Tasks Configuration

Various ENABLE_* flags for background tasks:
- **ENABLE_CLEAN_EMBEDDING_CACHE_TASK**: Clean expired embedding caches at 2AM daily
- **ENABLE_CLEAN_UNUSED_DATASETS_TASK**: Clean unused datasets at 3AM daily
- **ENABLE_CLEAN_MESSAGES**: Clean expired messages at 4AM daily
- **WORKFLOW_LOG_CLEANUP_ENABLED**: Clean workflow logs exceeding retention period
- **WORKFLOW_LOG_RETENTION_DAYS**: Default 30 days

## Other Settings

- **INVITE_EXPIRY_HOURS**: Invitation link validity, default 72 hours
- **HTTP_REQUEST_NODE_MAX_TEXT_SIZE**: Max text for HTTP request node, default 1MB
- **HTTP_REQUEST_NODE_MAX_BINARY_SIZE**: Max binary for HTTP request node, default 10MB
