#!/bin/bash

BACKUP_DIR="/backup/$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR

echo "Starting backup to $BACKUP_DIR..."

docker exec cloud-platform-mysql-1 mysqldump -u root -p${MYSQL_ROOT_PASSWORD} cloud_platform > $BACKUP_DIR/database.sql

docker exec cloud-platform-minio-1 mc mirror local/cloud-files $BACKUP_DIR/files

echo "Backup completed successfully!"
echo "Backup location: $BACKUP_DIR"
