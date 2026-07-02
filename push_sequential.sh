#!/bin/bash
cd /Users/yogeshkhangode/experiment-personal/Enterprise-Retail-Streaming-Platform/retail-streaming-platform

echo "Deleting remote main branch..."
git push origin --delete main 2>&1 || echo "Branch may not exist, continuing..."

echo ""
echo "Pushing all 1000 commits sequentially..."

# Get all commit hashes from oldest to newest
git log --oneline --format="%H" > /tmp/commits.txt
TOTAL=$(wc -l < /tmp/commits.txt)

# Push each commit one by one
COUNT=0
while read HASH; do
    COUNT=$((COUNT + 1))
    git push origin $HASH:refs/heads/main 2>&1
    if [ $? -eq 0 ]; then
        MSG=$(git log --oneline -1 $HASH)
        echo "[$COUNT/$TOTAL] Pushed: $MSG"
    else
        echo "[$COUNT/$TOTAL] FAILED!"
        break
    fi
done < /tmp/commits.txt

echo ""
echo "Done!"