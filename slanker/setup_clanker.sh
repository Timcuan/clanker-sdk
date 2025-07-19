#!/bin/bash

# Slanker Setup Script
# This script sets up the Clanker SDK and Node.js dependencies for token deployment

set -e

echo "🚀 Setting up Slanker with Clanker SDK..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    echo "Visit: https://nodejs.org/"
    exit 1
fi

# Check Node.js version
NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "❌ Node.js version 18 or higher is required. Current version: $(node --version)"
    exit 1
fi

echo "✅ Node.js $(node --version) detected"

# Check if npm is available
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not available. Please install npm."
    exit 1
fi

# Create a temporary directory for Clanker SDK setup
TEMP_DIR=$(mktemp -d)
cd "$TEMP_DIR"

echo "📦 Installing Clanker SDK and dependencies..."

# Initialize package.json
cat > package.json << 'EOF'
{
  "name": "slanker-clanker-setup",
  "version": "1.0.0",
  "type": "module",
  "dependencies": {
    "clanker-sdk": "^4.1.6",
    "viem": "^2.7.9"
  }
}
EOF

# Install dependencies
npm install

echo "🔧 Creating global symlinks..."

# Create global directory if it doesn't exist
GLOBAL_NODE_MODULES="/usr/local/lib/node_modules"
if [ ! -d "$GLOBAL_NODE_MODULES" ]; then
    sudo mkdir -p "$GLOBAL_NODE_MODULES"
fi

# Copy node_modules to global location for system-wide access
sudo cp -r node_modules/clanker-sdk "$GLOBAL_NODE_MODULES/"
sudo cp -r node_modules/viem "$GLOBAL_NODE_MODULES/"

# Create a simple test script
cat > test_clanker.js << 'EOF'
import { Clanker } from 'clanker-sdk';
import { createPublicClient, http } from 'viem';
import { base } from 'viem/chains';

console.log('✅ Clanker SDK imported successfully');
console.log('✅ Viem imported successfully');

const publicClient = createPublicClient({
    chain: base,
    transport: http('https://mainnet.base.org'),
});

console.log('✅ Base network client created');
console.log('🎉 Clanker SDK setup complete!');
EOF

# Test the installation
echo "🧪 Testing Clanker SDK installation..."
node test_clanker.js

# Cleanup
cd /
rm -rf "$TEMP_DIR"

echo ""
echo "🎉 Slanker setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Set up your environment variables in .env file"
echo "2. Start the API server: cd api && uvicorn main:app --reload"
echo "3. Start the Telegram bot: cd bot && python main.py"
echo "4. Serve the webapp: cd webapp && python -m http.server 8080"
echo ""
echo "For production deployment, use the provided render.yaml or Procfile"
echo ""