#!/bin/bash

# Configuration
API_URL="https://internal.intao.app/api/services/teams/send-message/git"
REPO_NAME=$(basename $(git rev-parse --show-toplevel))
BRANCH=$(git rev-parse --abbrev-ref HEAD)
COMMIT_HASH=$(git rev-parse HEAD)
COMMIT_MSG=$(git log -1 --pretty=%B)
AUTHOR=$(git log -1 --pretty=%an)
COMPARE_URL="https://github.com/$(git config --get remote.origin.url | sed 's/.*github.com[:/]//' | sed 's/\.git$//')/compare/$(git rev-parse HEAD~1)...$(git rev-parse HEAD)"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're on main branch
if [ "$BRANCH" != "main" ]; then
    echo -e "${YELLOW}Not on main branch, skipping Teams notification${NC}"
    exit 0
fi

# Prepare the payload
PAYLOAD="{
    \"repository\": \"$REPO_NAME\",
    \"branch\": \"$BRANCH\",
    \"commits\": [{
        \"id\": \"$COMMIT_HASH\",
        \"message\": \"$COMMIT_MSG\"
    }],
    \"author\": \"$AUTHOR\",
    \"compare_url\": \"$COMPARE_URL\",
    \"action\": \"push\"
}"

# Send notification to Teams
echo -e "${GREEN}Sending notification to Teams...${NC}"
curl -H "Content-Type: application/json" \
     -d "$PAYLOAD" \
     "$API_URL"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}Teams notification sent successfully!${NC}"
else
    echo -e "${RED}Failed to send Teams notification${NC}"
    exit 1
fi 