#!/bin/bash

echo "Installing Cloud-Platform..."

if ! command -v docker &> /dev/null; then
    echo "Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

cd "$(dirname "$0")/../docker"

echo "Pulling Docker images..."
docker-compose pull

echo "Building custom images..."
docker-compose build

echo "Creating necessary directories..."
mkdir -p /backup

echo "Installation completed!"
echo "Run './start.sh' to start the services."
