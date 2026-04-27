#!/bin/bash
set -e

# 安装 pgvector（如果尚未安装）
if ! apk info postgresql-pgvector > /dev/null 2>&1; then
    apk add --no-cache postgresql-pgvector
fi

# 启动 PostgreSQL
exec docker-entrypoint.sh postgres
