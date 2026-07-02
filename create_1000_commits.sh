#!/bin/bash
cd /Users/yogeshkhangode/experiment-personal/Enterprise-Retail-Streaming-Platform/retail-streaming-platform

# Remove the script files from being tracked - only track the actual project
git rm --cached create_1000.sh create_commits.sh 2>/dev/null || true

# Create a tracking file
echo "# Commit History" > commit_history.txt

# June 24, 2026 to July 1, 2026
START_EPOCH=1782321022  # June 24, 2026 22:40:22 IST
INTERVAL=605            # ~10 minutes between commits

echo "Creating 1000 commits from June 24, 2026 to July 1, 2026..."

for i in $(seq 0 999); do
    COMMIT_EPOCH=$(( START_EPOCH + (i * INTERVAL) ))
    COMMIT_DATE=$(date -r $COMMIT_EPOCH "+%Y-%m-%d %H:%M:%S")
    
    echo "Commit $i at $COMMIT_DATE" >> commit_history.txt
    git add commit_history.txt
    GIT_COMMITTER_DATE="$COMMIT_DATE" GIT_AUTHOR_DATE="$COMMIT_DATE" \
        git commit -m "build: commit $(printf "%04d" $i) - $(date -r $COMMIT_EPOCH "+%b %d, %Y")" --allow-empty
    
    if [ $((i % 100)) -eq 0 ]; then
        echo "  Progress: $i / 1000"
    fi
done

echo ""
echo "Done! Total commits: $(git rev-list --all --count)"
echo ""
echo "First commit:"
git log --oneline --format="%ci %s" | tail -1
echo ""
echo "Last commit:"
git log --oneline --format="%ci %s" | head -1