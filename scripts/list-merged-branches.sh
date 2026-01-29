#!/bin/bash

# Script to list all branches that have been merged into main
# Usage: ./scripts/list-merged-branches.sh

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Branches Merged with Main${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Ensure we have the latest main branch
echo -e "${YELLOW}Fetching latest main branch...${NC}"
git fetch origin main:main --quiet 2>/dev/null || true
echo ""

# Get the list of merge commits
echo -e "${GREEN}Extracting merged branches from Git history...${NC}"
echo ""

# Show merge commits with PR numbers
echo -e "${BLUE}=== Merge Commits (by PR number) ===${NC}"
git log --merges --oneline main --pretty=format:"%s" | grep "Merge pull request" | nl
echo ""
echo ""

# Show unique branch names sorted
echo -e "${BLUE}=== Unique Branch Names (alphabetically) ===${NC}"
git log --merges --oneline main --pretty=format:"%s" | \
    grep "Merge pull request" | \
    sed 's/Merge pull request #[0-9]* from pat-the-geek\///' | \
    sort -u | \
    nl
echo ""

# Count total merged branches
TOTAL_COUNT=$(git log --merges --oneline main --pretty=format:"%s" | grep -c "Merge pull request" || echo "0")
echo -e "${GREEN}Total merged branches: ${TOTAL_COUNT}${NC}"
echo ""

# Offer to update documentation
echo -e "${YELLOW}To update the documentation file, run:${NC}"
echo -e "  ${BLUE}./scripts/update-merged-branches-doc.sh${NC}"
echo ""
