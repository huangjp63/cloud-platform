#!/bin/bash

echo "Stopping Cloud-Platform services..."

cd "$(dirname "$0")/../docker"

docker-compose down

echo "Services stopped successfully!"
