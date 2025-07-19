#!/bin/bash

# Slanker Quick Start Script
# This script helps you get started with Slanker development quickly

set -e

echo "🚀 Slanker Quick Start"
echo "======================"

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚙️  Setting up environment file..."
    cp .env.example .env
    echo "✅ Created .env file from template"
    echo "⚠️  Please edit .env with your actual values before continuing!"
    echo ""
    echo "Required variables:"
    echo "- TELEGRAM_BOT_TOKEN (get from @BotFather)"
    echo "- PRIVATE_KEY (your Ethereum private key)"
    echo "- API_SECRET_KEY (any random string)"
    echo ""
    read -p "Press Enter when you've configured .env file..."
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js 18+ first."
    echo "Visit: https://nodejs.org/"
    exit 1
fi

# Check if Python is available
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "❌ Python not found. Please install Python 3.9+ first."
    exit 1
fi

echo "📦 Installing dependencies..."

# Install Node.js dependencies
if [ ! -d "node_modules" ]; then
    echo "Installing Node.js packages..."
    npm install
fi

# Setup Clanker SDK
echo "Setting up Clanker SDK..."
./setup_clanker.sh

# Install Python dependencies
echo "Installing Python dependencies..."
if [ -d "api" ]; then
    cd api && pip install -r requirements.txt && cd ..
fi
if [ -d "bot" ]; then
    cd bot && pip install -r requirements.txt && cd ..
fi

echo ""
echo "🎉 Setup completed!"
echo ""
echo "To start development:"
echo ""
echo "Terminal 1 (API Server):"
echo "  npm run dev:api"
echo ""
echo "Terminal 2 (Telegram Bot):"
echo "  npm run dev:bot"
echo ""
echo "Terminal 3 (WebApp):"
echo "  npm run dev:webapp"
echo ""
echo "Then:"
echo "- Open http://localhost:8080 for WebApp"
echo "- Send /slanker to your Telegram bot"
echo ""
echo "📖 For deployment instructions, see DEPLOYMENT.md"
echo ""