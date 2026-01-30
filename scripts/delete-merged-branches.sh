#!/bin/bash
#
# Script to delete all merged branches from GitHub
# This script should be run by a user with push access to the repository
#
# Usage: ./scripts/delete-merged-branches.sh
#

set -e

# List of merged branches to delete (identified from closed PRs)
MERGED_BRANCHES=(
    "copilot/implement-second-step-programming"
    "copilot/fix-click-module-error"
    "copilot/list-merged-branches"
    "copilot/check-library-dependencies"
    "copilot/implement-issue-59-solution"
    "copilot/prepare-design-report"
    "copilot/update-documents-for-timeline-roon"
    "copilot/fix-timeline-roon-code"
    "copilot/fix-display-issues"
    "copilot/propose-roon-journal-interface"
    "copilot/organize-main-directory-files"
    "copilot/fix-zero-tracks-issue"
    "copilot/fix-tracks-analysis-issue"
    "copilot/verify-report-data-issue-47"
    "copilot/fix-calculation-errors"
    "copilot/modify-code-according-to-document"
    "copilot/analyze-issue-41"
    "copilot/prepare-data-model-for-sqlite-migration"
    "copilot/update-docs-todo-roadmap"
    "copilot/fix-playlist-duplicates"
    "copilot/check-roon-api-playlist-functionality"
    "copilot/update-roadmap-and-todo-list"
    "copilot/improve-tests-based-on-issue-28"
    "copilot/fix-time-issue"
    "copilot/check-test-status"
    "copilot/continue-test-implementation"
    "copilot/fix-correct-collection-issue"
    "copilot/update-coherence-check"
    "copilot/update-roadmap-and-docs"
    "copilot/fix-246838957-1141348123-1143eb3b-6dc7-42ae-9e2b-6ea93ddca748"
    "copilot/fix-issue-21-tracker"
    "copilot/analyse-revues-modifications"
    "copilot/fix-issue-15-collection-errors"
    "copilot/improve-user-interface-design"
    "copilot/fix-haiku-markdown-display"
    "copilot/fix-haiku-display-issues"
    "copilot/create-task-scheduler-module"
    "copilot/update-last-order-status"
    "copilot/create-scheduler-module"
    "copilot/improve-ui-layout-history"
    "copilot/prioritize-tasks-for-project"
    "copilot/analyse-code-architecture"
)

echo "=========================================="
echo "Deleting ${#MERGED_BRANCHES[@]} merged branches"
echo "=========================================="
echo ""

DELETED_COUNT=0
FAILED_COUNT=0
FAILED_BRANCHES=()

for branch in "${MERGED_BRANCHES[@]}"; do
    echo "Deleting branch: $branch"
    if git push origin --delete "$branch" 2>&1; then
        echo "✅ Successfully deleted: $branch"
        ((DELETED_COUNT++))
    else
        echo "❌ Failed to delete: $branch"
        ((FAILED_COUNT++))
        FAILED_BRANCHES+=("$branch")
    fi
    echo ""
done

echo ""
echo "=========================================="
echo "Summary"
echo "=========================================="
echo "Total branches processed: ${#MERGED_BRANCHES[@]}"
echo "Successfully deleted: $DELETED_COUNT"
echo "Failed to delete: $FAILED_COUNT"

if [ $FAILED_COUNT -gt 0 ]; then
    echo ""
    echo "Failed branches:"
    for branch in "${FAILED_BRANCHES[@]}"; do
        echo "  - $branch"
    done
fi

echo ""
echo "Cleaning up local references to deleted branches..."
git fetch --prune origin

echo ""
echo "Done! ✨"
