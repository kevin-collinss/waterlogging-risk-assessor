#!/bin/bash

# Start the backend server
echo "Starting backend..."
node backend/server.js &

# Save the PID of the backend process
BACKEND_PID=$!

# Navigate to the frontend directory
cd ./frontend/frontend || exit

# Start the frontend
echo "Starting frontend..."
npm start