#!/bin/bash

# Get the list of service directories
service_directories=$(find services -mindepth 1 -maxdepth 1 -type d)

# Loop through each service directory and run docker-compose up -d
for service_dir in $service_directories; do
    echo "Starting service in directory: $service_dir"
    docker-compose -f "$service_dir/docker-compose.yml" up -d
done
