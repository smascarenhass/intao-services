#!/bin/bash

echo "🔧 Setting up Git hooks..."

HOOKS_DIR=".git/hooks"
CUSTOM_HOOKS_DIR="git/githooks"
SCRIPTS_DIR="git/scripts"
CONFIG_DIR="git/config"

# Create necessary directories
mkdir -p "$SCRIPTS_DIR"

# Copy the pre-push hook from shared directory
cp "$CUSTOM_HOOKS_DIR/pre-push" "$HOOKS_DIR/pre-push"
chmod +x "$HOOKS_DIR/pre-push"

# Copy the Teams notification script
cp "$CUSTOM_HOOKS_DIR/notify-teams.sh" "$SCRIPTS_DIR/notify-teams.sh"
chmod +x "$SCRIPTS_DIR/notify-teams.sh"

# Copy the deploy script
cp "$CUSTOM_HOOKS_DIR/deploy.sh" "$SCRIPTS_DIR/deploy.sh"
chmod +x "$SCRIPTS_DIR/deploy.sh"

# Copy example environment file if .env doesn't exist
if [ ! -f ".env" ]; then
    cp "$CONFIG_DIR/.env.example" ".env"
    echo "⚠️  Please review and update the .env file with your project's configuration"
fi

echo "✅ Git hooks installed successfully."
