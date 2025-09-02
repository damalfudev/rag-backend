#!/bin/bash

echo "Starting Multimodal RAG Docker Simulation..."

# Build and start the container
docker-compose up --build -d

echo "Container started. API available at http://localhost:8000"
echo "API documentation at http://localhost:8000/docs"

# Wait for container to be ready
sleep 10

echo "Testing API..."
python test_api.py

echo "Simulation ready!"
echo "To stop: docker-compose down"
