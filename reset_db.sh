#!/bin/bash

# Stop the Flask application (if running)
# pkill -f flask  # Uncomment if needed

# For SQLite
rm -f instance/app.db

# For PostgreSQL (uncomment and modify if using PostgreSQL)
# psql -U postgres -c "DROP DATABASE IF EXISTS your_database_name;"
# psql -U postgres -c "CREATE DATABASE your_database_name;"

# Remove old migrations
rm -rf migrations/

# Initialize new database
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# Run initialization script
python init_db.py

echo "Database reset complete!"