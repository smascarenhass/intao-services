#!/bin/bash

echo "🔧 Setting up Git hooks..."

HOOKS_DIR=".git/hooks"
CUSTOM_HOOKS_DIR="git/githooks"
SCRIPTS_DIR="scripts"

# Create scripts directory if it doesn't exist
mkdir -p "$SCRIPTS_DIR"

# Copy the pre-push hook from shared directory
cp "$CUSTOM_HOOKS_DIR/pre-push" "$HOOKS_DIR/pre-push"
chmod +x "$HOOKS_DIR/pre-push"

# Copy the Teams notification script
cp "$CUSTOM_HOOKS_DIR/notify-teams.sh" "$SCRIPTS_DIR/notify-teams.sh"
chmod +x "$SCRIPTS_DIR/notify-teams.sh"

echo "✅ Git hooks installed successfully."
