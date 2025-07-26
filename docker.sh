#!/bin/bash

# Docker helper script for Adobe PDF Processor

case "$1" in
    "build")
        echo "Building Docker image..."
        docker build -t adobe-pdf-processor .
        ;;
    "run")
        echo "Running PDF processor..."
        docker-compose up --build
        ;;
    "shell")
        echo "Opening interactive shell in container..."
        docker run -it --rm \
            -v "$(pwd)/input:/app/input:ro" \
            -v "$(pwd)/output:/app/output:rw" \
            adobe-pdf-processor /bin/bash
        ;;
    "clean")
        echo "Cleaning up Docker resources..."
        docker-compose down
        docker rmi adobe-pdf-processor 2>/dev/null || true
        ;;
    *)
        echo "Usage: $0 {build|run|shell|clean}"
        echo ""
        echo "Commands:"
        echo "  build  - Build the Docker image"
        echo "  run    - Run the PDF processor using docker-compose"
        echo "  shell  - Open an interactive shell in the container"
        echo "  clean  - Clean up Docker resources"
        exit 1
        ;;
esac
