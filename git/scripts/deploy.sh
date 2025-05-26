#!/bin/bash

ENV_PATH="git/config/.env"
if [ -f "$ENV_PATH" ]; then
    source "$ENV_PATH"
fi

# Configuration
REMOTE_USER="intao"
REMOTE_HOST="internal.intao.app"
REMOTE_DIR="/home/intao/intao-services"
LOCAL_DIR="."

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting deployment...${NC}"

# Sync files using rsync with password
echo -e "${GREEN}Syncing files to remote server...${NC}"
rsync -avz --exclude 'venv' \
           --exclude '.git' \
           --exclude '__pycache__' \
           --exclude '*.pyc' \
           --exclude '.env' \
           --exclude '.DS_Store' \
           "$LOCAL_DIR/" "$REMOTE_USER@$REMOTE_HOST:$REMOTE_DIR/"

# Check if rsync was successful
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Files synced successfully${NC}"
else
    echo -e "${RED}Failed to sync files${NC}"
    exit 1
fi

# SSH into the server and restart the services
echo -e "${GREEN}Restarting services...${NC}"
ssh "$REMOTE_USER@$REMOTE_HOST" "cd $REMOTE_DIR && \
    if command -v docker-compose &> /dev/null; then \
        docker-compose down && docker-compose up -d --build; \
    elif command -v docker &> /dev/null; then \
        docker compose down && docker compose up -d --build; \
    else \
        echo 'Docker not found. Please install Docker and Docker Compose.'; \
        exit 1; \
    fi"

# Check if SSH commands were successful
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Deployment completed successfully!${NC}"
    
    # Send Teams notification if script exists
    if [ -f "scripts/notify-teams.sh" ]; then
        echo -e "${GREEN}Sending Teams notification...${NC}"
        bash scripts/notify-teams.sh
    fi
else
    echo -e "${RED}Failed to restart services${NC}"
    exit 1
fi 