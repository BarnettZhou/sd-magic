#!/bin/bash

# Get script directory
dirname=$(dirname "$0")
script_dir=$(cd "$dirname" && pwd)

# Get timestamp
timestamp=$(date +%Y%m%d_%H%M%S)

# Create backup directory if it doesn't exist
backup_dir="$script_dir/../backup"
mkdir -p "$backup_dir"

# Create timestamped backup file
backup_file="$backup_dir/backup_$timestamp.sql"

docker exec -i sd-magic-db-1 pg_dump -U sdmagic sdmagic > "$backup_file"

echo "Database backup completed successfully."
echo "Backup file: $backup_file"
echo "Backup directory: $backup_dir"