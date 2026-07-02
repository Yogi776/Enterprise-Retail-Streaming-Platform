#!/bin/bash
cd /Users/yogeshkhangode/experiment-personal/Enterprise-Retail-Streaming-Platform/retail-streaming-platform

TOTAL=$(git rev-list --all --count)
echo "Pushing $TOTAL commits one by one..."

for i in $(seq 1 $TOTAL); do
    # Get the i-th commit from oldest
    HASH=$(git log --oneline --format="%H" | tail -$i | head -1)
    MSG=$(git log --oneline --format="%s" -1 $HASH)
    DATE=$(git log --format="%ci" -1 $HASH)
    
    # Push this specific commit
    git push origin $HASH:main 2>&1
    
    if [ $? -eq 0 ]; then
        echo "[$i/$TOTAL] Pushed: $MSG ($DATE)"
    else
        echo "[$i/$TOTAL] FAILED: $MSG"
        break
    fi
done

echo ""
echo "Push complete!"