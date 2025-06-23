#!/bin/bash

# ParkBench Platform Startup Script
# This script starts both the backend API and frontend portal

echo "🚀 Starting ParkBench Platform..."
echo "=================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Start backend services (Docker Compose)
echo "📦 Starting backend services..."
cd parkbench/deployment
docker compose up -d

# Wait for backend to be healthy
echo "🔍 Waiting for backend API to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:9000/health > /dev/null 2>&1; then
        echo "✅ Backend API is ready!"
        break
    fi
    echo "   Waiting for backend... ($i/30)"
    sleep 2
done

# Check if backend is ready
if ! curl -s http://localhost:9000/health > /dev/null 2>&1; then
    echo "❌ Backend API failed to start. Check Docker logs:"
    docker compose logs backend
    exit 1
fi

# Start frontend development server
echo "🎨 Starting frontend portal..."
cd ../frontend/parkbench-portal

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    npm install
fi

# Start frontend in background
npm start &
FRONTEND_PID=$!

# Wait for frontend to be ready
echo "🔍 Waiting for frontend to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        echo "✅ Frontend is ready!"
        break
    fi
    echo "   Waiting for frontend... ($i/30)"
    sleep 2
done

echo ""
echo "🎉 ParkBench Platform is now running!"
echo "=================================="
echo "📊 Frontend Portal: http://localhost:3000"
echo "🔧 Backend API:     http://localhost:9000"
echo "📚 API Docs:        http://localhost:9000/docs"
echo "🗄️  Database:       localhost:5433 (postgres/password)"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping ParkBench Platform..."
    
    # Stop frontend
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
    fi
    
    # Stop backend
    cd ../../parkbench/deployment
    docker compose down
    
    echo "✅ All services stopped"
    exit 0
}

# Set trap to cleanup on Ctrl+C
trap cleanup SIGINT SIGTERM

# Keep script running
wait $FRONTEND_PID 