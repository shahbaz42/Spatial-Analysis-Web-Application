#!/bin/bash
set -e

echo "=================================="
echo "Solar Site Analyzer - Starting API"
echo "=================================="

# Wait for MySQL to be ready
echo "Waiting for MySQL to be ready..."
while ! mysqladmin ping -h"$DB_HOST" -P"$DB_PORT" -u"$DB_USER" -p"$DB_PASSWORD" --skip-ssl --silent 2>/dev/null; do
    echo "MySQL is unavailable - sleeping"
    sleep 2
done

echo "MySQL is up and ready!"

# Check if database needs initialization
echo "Checking database status..."

# First check if the database exists
DB_EXISTS=$(mysql -h"$DB_HOST" -P"$DB_PORT" -u"$DB_USER" -p"$DB_PASSWORD" --skip-ssl -e "SELECT SCHEMA_NAME FROM information_schema.SCHEMATA WHERE SCHEMA_NAME = '$DB_NAME';" -s -N 2>/dev/null || echo "")

if [ -z "$DB_EXISTS" ]; then
    echo "Database does not exist. Creating and initializing..."
    NEEDS_INIT=true
else
    # Database exists, check if sites table has data
    SITE_COUNT=$(mysql -h"$DB_HOST" -P"$DB_PORT" -u"$DB_USER" -p"$DB_PASSWORD" --skip-ssl -D"$DB_NAME" -e "SELECT COUNT(*) FROM sites;" -s -N 2>/dev/null || echo "0")
    
    if [ "$SITE_COUNT" = "0" ]; then
        echo "Database exists but has no data. Running initialization..."
        NEEDS_INIT=true
    else
        echo "Database already initialized with $SITE_COUNT sites. Skipping initialization."
        NEEDS_INIT=false
    fi
fi

if [ "$NEEDS_INIT" = "true" ]; then
    echo "Running database initialization..."
    
    # Drop and recreate database to ensure clean state (use root for admin operations)
    echo "Dropping existing database (if any) for clean initialization..."
    mysql -h"$DB_HOST" -P"$DB_PORT" -uroot -p"$DB_PASSWORD" --skip-ssl -e "DROP DATABASE IF EXISTS $DB_NAME; CREATE DATABASE $DB_NAME;" 2>&1 | grep -v "Warning: Using a password on the command line" || true
    
    # Grant privileges to the application user
    echo "Granting privileges to $DB_USER..."
    mysql -h"$DB_HOST" -P"$DB_PORT" -uroot -p"$DB_PASSWORD" --skip-ssl -e "GRANT ALL PRIVILEGES ON $DB_NAME.* TO '$DB_USER'@'%'; FLUSH PRIVILEGES;" 2>&1 | grep -v "Warning: Using a password on the command line" || true
    
    # Import schema
    echo "Importing database schema..."
    mysql -h"$DB_HOST" -P"$DB_PORT" -u"$DB_USER" -p"$DB_PASSWORD" --skip-ssl < /app/databaseschema.sql
    
    # Load initial data
    echo "Loading initial data from CSV..."
    python /app/scripts/init_database.py
    
    echo "Database initialization completed!"
fi

# Start the application
echo "Starting FastAPI application..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
