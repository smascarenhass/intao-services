#!/bin/bash

echo "🔧 Setting up Git hooks..."

HOOKS_DIR=".git/hooks"
CUSTOM_HOOKS_DIR="git/githooks"

# Copy the pre-push hook from shared directory
cp "$CUSTOM_HOOKS_DIR/pre-push" "$HOOKS_DIR/pre-push"
chmod +x "$HOOKS_DIR/pre-push"

echo "✅ Git hooks installed successfully."
