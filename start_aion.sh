#!/bin/bash

echo "🦞 Awakening Aion__Prime..."

# Check if PM2 is installed
if ! command -v pm2 &> /dev/null; then
    echo "⚠️  PM2 not found. Installing..."
    npm install pm2 -g
fi

# Start Ecosystem
pm2 start ecosystem.config.cjs

echo "✅ AION ONLINE."
echo "📊 Dashboard: http://localhost:3333"
echo "👁️  Monitor:   pm2 monit"
