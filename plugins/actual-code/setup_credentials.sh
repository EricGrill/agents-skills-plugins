#!/bin/bash
# Setup script for Google Cloud credentials

echo "🔐 Google Cloud Authentication Setup"
echo "======================================"
echo ""
echo "Choose an option:"
echo "  1) Use service account key file"
echo "  2) Install gcloud CLI (recommended)"
echo ""
read -p "Enter your choice (1 or 2): " choice

if [ "$choice" = "1" ]; then
    echo ""
    read -p "Enter the path to your service account key JSON file: " key_path
    
    if [ -f "$key_path" ]; then
        export GOOGLE_APPLICATION_CREDENTIALS="$key_path"
        echo ""
        echo "✅ Credentials set!"
        echo ""
        echo "Add this to your .env file:"
        echo "GOOGLE_APPLICATION_CREDENTIALS=$key_path"
        echo ""
        echo "Or run this command to set it for this session:"
        echo "export GOOGLE_APPLICATION_CREDENTIALS=\"$key_path\""
    else
        echo "❌ File not found: $key_path"
        exit 1
    fi
    
elif [ "$choice" = "2" ]; then
    echo ""
    echo "Installing Google Cloud CLI via Homebrew..."
    
    if ! command -v brew &> /dev/null; then
        echo "❌ Homebrew not found. Install it from https://brew.sh"
        exit 1
    fi
    
    brew install google-cloud-sdk
    
    echo ""
    echo "✅ gcloud CLI installed!"
    echo ""
    echo "Now run these commands:"
    echo "  gcloud auth application-default login"
    echo "  gcloud config set project ActualCode"
    
else
    echo "Invalid choice"
    exit 1
fi
