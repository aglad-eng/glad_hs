#!/bin/bash

# Check if an argument is provided
if [ -z "$1" ]; then
    echo "Please provide an argument: 'up' or 'down'"
    exit 1
fi

# Get the list of service directories
service_directories=$(find services -mindepth 1 -maxdepth 1 -type d)

# Loop through each service directory and run docker-compose up -d
for service_dir in $service_directories; do
    echo "Starting service in directory: $service_dir"
    docker-compose -f "$service_dir/docker-compose.yml" up -d
    # Check the provided argument
    case "$1" in
        "up")
            # Start containers in the background
            docker-compose -f "$service_dir/docker-compose.yml" up -d
            ;;
        "down")
            # Stop and remove containers
            docker-compose -f "$service_dir/docker-compose.yml" down
            ;;
        *)
            echo "Invalid argument. Please use 'up' or 'down'"
            exit 1
            ;;
    esac
done
