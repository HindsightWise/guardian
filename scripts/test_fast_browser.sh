#!/bin/bash
# Test script for fast-browser-use skill verification

BINARY="${HOME}/.cargo/bin/fast-browser-use"

if [ ! -f "$BINARY" ]; then
    echo "Error: fast-browser-use binary not found at $BINARY"
    echo "Checking PATH..."
    if command -v fast-browser-use &> /dev/null; then
        BINARY=$(command -v fast-browser-use)
    else
        echo "fast-browser-use not found in PATH."
        # Fallback to local build artifact if available
        LOCAL_BIN="skills/fast-browser-use/target/release/fast-browser-use"
        if [ -f "$LOCAL_BIN" ]; then
             BINARY="$LOCAL_BIN"
             echo "Using local build artifact: $BINARY"
        else
             exit 1
        fi
    fi
fi

echo "Using binary: $BINARY"

# 1. Navigation & Screenshot
echo "1. Testing Screenshot (google.com)..."
"$BINARY" screenshot --url "https://google.com" --output "test_google.png"

# 2. Extract DOM
echo "2. Testing Metadata Extraction..."
"$BINARY" sitemap --url "https://google.com" > test_sitemap.json

echo "Verification Complete."
ls -l test_google.png test_sitemap.json
