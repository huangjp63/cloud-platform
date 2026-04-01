#!/bin/bash

echo "Starting Cloud-Platform services..."

cd "$(dirname "$0")/../docker"

docker-compose up -d

echo "Waiting for services to be ready..."
sleep 10

echo "Services started successfully!"
echo "Frontend: http://localhost"
echo "Backend API: http://localhost:8000/docs"
echo "Kibana: http://localhost:5601"
echo "MinIO Console: http://localhost:9001"
