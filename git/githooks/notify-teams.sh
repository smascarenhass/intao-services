#!/bin/bash

# Configuration
TEAMS_WEBHOOK_URL=${TEAMS_WEBHOOK_URL:-""}
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

# Check if webhook URL is set
if [ -z "$TEAMS_WEBHOOK_URL" ]; then
    echo -e "${YELLOW}TEAMS_WEBHOOK_URL not set, skipping Teams notification${NC}"
    exit 0
fi

# Prepare the message
MESSAGE="## 🚀 New changes in $REPO_NAME\n\n"
MESSAGE+="**Branch:** $BRANCH\n"
MESSAGE+="**Author:** $AUTHOR\n"
MESSAGE+="**Action:** push\n\n"
MESSAGE+="### 📝 Commit:\n\n"
MESSAGE+="- $COMMIT_MSG ($COMMIT_HASH)\n\n"
MESSAGE+="[View changes]($COMPARE_URL)"

# Send notification to Teams
echo -e "${GREEN}Sending notification to Teams...${NC}"
curl -H "Content-Type: application/json" \
     -d "{\"text\": \"$MESSAGE\"}" \
     "$TEAMS_WEBHOOK_URL"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}Teams notification sent successfully!${NC}"
else
    echo -e "${RED}Failed to send Teams notification${NC}"
    exit 1
fi 