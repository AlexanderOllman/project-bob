#!/bin/bash

echo "Pulling latest..."
git pull

echo "Building image..."
docker build -t fheonix/project-bob:0.0.1 .

echo "Pushing image..."
docker push fheonix/project-bob:0.0.1

echo "Done."





