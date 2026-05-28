#!/bin/bash
# setup.sh — One-command dev environment setup
set -e

echo "🚀 Setting up AWS Cost Optimization Dashboard..."

# Backend
echo "📦 Installing Python dependencies..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt --quiet
cd ..

# Generate sample data for demo mode
echo "📊 Generating sample data..."
python3 scripts/generate_sample_data.py
cp scripts/sample_data.json frontend/public/sample_data.json

# Frontend
echo "🎨 Installing frontend dependencies..."
cd frontend
npm install --silent
cd ..

echo ""
echo "✅ Setup complete!"
echo ""
echo "  Start backend:   cd backend && source venv/bin/activate && python app.py"
echo "  Start frontend:  cd frontend && npm run dev"
echo "  Dashboard at:    http://localhost:5173"
echo ""
echo "  DEMO_MODE is ON by default — no AWS account needed."
echo "  Set DEMO_MODE=false in frontend/src/App.jsx to use real AWS."
