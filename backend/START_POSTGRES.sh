#!/bin/bash
# Manual PostgreSQL startup script

PG_DATA_DIR="/usr/local/var/postgresql@14"
if [ ! -d "$PG_DATA_DIR" ]; then
    PG_DATA_DIR="/opt/homebrew/var/postgresql@14"
fi

if [ ! -d "$PG_DATA_DIR" ]; then
    echo "❌ PostgreSQL data directory not found"
    echo "   Please initialize PostgreSQL first:"
    echo "   initdb $PG_DATA_DIR"
    exit 1
fi

echo "Starting PostgreSQL manually..."
pg_ctl -D "$PG_DATA_DIR" -l "$PG_DATA_DIR/server.log" start

sleep 3

if psql -h localhost -U $(whoami) -d postgres -c "SELECT 1;" > /dev/null 2>&1; then
    echo "✅ PostgreSQL started successfully"
else
    echo "❌ PostgreSQL failed to start"
    echo "   Check logs: tail -f $PG_DATA_DIR/server.log"
fi
