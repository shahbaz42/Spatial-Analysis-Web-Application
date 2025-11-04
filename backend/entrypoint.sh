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
DB_EXISTS=$(mysql -h"$DB_HOST" -P"$DB_PORT" -u"$DB_USER" -p"$DB_PASSWORD" --skip-ssl -e "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = '$DB_NAME' AND table_name = 'sites';" -s -N 2>/dev/null || echo "0")

if [ "$DB_EXISTS" = "0" ]; then
    echo "Database not initialized. Running initialization script..."
    
    # Import schema
    echo "Importing database schema..."
    mysql -h"$DB_HOST" -P"$DB_PORT" -u"$DB_USER" -p"$DB_PASSWORD" --skip-ssl < /app/databaseschema.sql
    
    # Load initial data
    echo "Loading initial data from CSV..."
    python /app/scripts/init_database.py
    
    echo "Database initialization completed!"
else
    echo "Database already initialized. Skipping initialization."
fi

# Start the application
echo "Starting FastAPI application..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
